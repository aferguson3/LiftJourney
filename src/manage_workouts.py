import dataclasses
import json
import logging
import queue
import re
import time
from threading import Thread

import garth

from src.models.ExerciseSet import ExerciseSet
from src.models.Workout import Workout
from src.utils import Endpoints

logger = logging.getLogger(__name__)
q = queue.Queue()


def workouts_to_dict(workouts_list: list[Workout]) -> dict:
    if isinstance(workouts_list, list) is not True:
        raise TypeError(f"{workouts_list} is not type list.")

    workouts = list()
    for workout in workouts_list:
        workout.set_data_validation_check()
        workouts.append(workout.asdict())
    return {"workouts": workouts}


def set_metadata(workouts_dict: dict, _metadata: dict):
    # Creates metadata from workouts previously sorted by date
    metadata = _metadata.copy()
    try:
        metadata["numWorkouts"] = len(workouts_dict["workouts"])
        metadata["dates"]["firstWorkout"] = workouts_dict["workouts"][0]["datetime"]
        metadata["dates"]["lastWorkout"] = workouts_dict["workouts"][-1]["datetime"]
    except KeyError as k:
        raise KeyError(f"{k}")
    return metadata


def dump_to_json(workout_data: dict, filepath: str, option, _metadata: dict = None):
    if isinstance(workout_data, dict) is not True:
        raise TypeError(f"{workout_data} is not type dict.")

    match option:
        case "a" | "w":
            try:
                with open(filepath, option) as file:
                    json.dump(workout_data, file, sort_keys=True)
            except FileNotFoundError:
                logger.error(f"{filepath} not found.")
                raise FileNotFoundError(f"{filepath} not found")

        case _:
            raise ValueError(f"Invalid option:{option} used in json.dump().")

    if _metadata is None:
        return

    logger.info("Metadata enabled.")
    try:
        metadata = set_metadata(workout_data, _metadata)
        filepath = metadata.pop("filepath")
        with open(filepath, 'w') as file:
            json.dump(metadata, file)
    except FileNotFoundError:
        logger.error(f"{filepath} not found.")
        raise FileNotFoundError(f"{filepath} not found")


def load_workouts(filepath: str) -> list[Workout]:
    try:
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            all_workouts = list()
            for workout in json_data["workouts"]:
                a_workout = Workout()
                a_workout.init_workout(workout)
                all_workouts.append(a_workout)
        return all_workouts

    except FileNotFoundError as e:
        logger.error(f"{e}")
        raise FileNotFoundError(f"{e}")


def sort_workouts(workout_data: Workout | list[Workout], key: str, reverse=False) \
        -> list[ExerciseSet | Workout] | None:
    searchedData, isValidKey = None, None
    if isinstance(workout_data, list):
        isValidKey = hasattr(workout_data[0], key)
        searchedData = workout_data
    elif isinstance(workout_data, Workout):
        isValidKey = hasattr(workout_data.sets[0], key)
        searchedData = workout_data.sets

    if isValidKey:
        try:
            sorted_list = sorted(searchedData, key=lambda w: getattr(w, key), reverse=reverse)
            return sorted_list
        except TypeError as msg:
            logger.error(f"{msg}")
            raise TypeError(f"{msg}")

    else:
        logger.error(f"Sorting {type(workout_data)} by key: {key} FAILED.")

    return None


def view_sets_from_workouts(workout_data: list[Workout]) -> dict:
    # Returns dict of all workouts sets
    if isinstance(workout_data, list) is not True:
        raise TypeError(f"{workout_data} is not type list.")

    _dict = dict()
    for field in dataclasses.fields(ExerciseSet):
        field_data = [getattr(_set, field.name) for wo in workout_data for _set in wo.sets]
        _dict[str(field.name)] = field_data

    return _dict


def fill_out_workouts(workouts: list[Workout]) -> list[Workout]:
    # Fills out targetReps and missing exerciseNames using scheduled workout info
    start = time.perf_counter()
    threads, num_threads = [], 10  # Max 10 threads
    splice = int(len(workouts) / num_threads)
    workouts_rv = []

    if len(workouts) < num_threads:
        for wo in workouts:
            t = Thread(target=_fill_out_workouts, args=[wo])
            threads.append(t)
    else:
        for i in range(0, num_threads):
            cur_index = i * splice
            t = Thread(target=_fill_out_workouts, args=[workouts[cur_index: cur_index + splice]])
            threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    while not q.empty():
        workouts_rv = workouts_rv + q.get()

    end = time.perf_counter()
    logger.info(f"{(end - start):.2f} seconds to fill out workouts")
    return workouts_rv


def _fill_out_workouts(workouts: list[Workout] | Workout):
    pattern = r"\b\d+(?:\.\d+)+\b"
    if isinstance(workouts, Workout):
        workouts = [workouts]

    for wo in workouts:
        garmin_data = garth.connectapi(f"{Endpoints.garmin_connect_activity}/{wo.activityId}/workouts")[0]
        workout_name_str = garmin_data["workoutName"]

        version_str = re.search(pattern, workout_name_str)
        version_str = version_str.group() if version_str is not None else None
        workout_name = re.sub(pattern, '', workout_name_str).strip()
        wo.version = version_str
        wo.name = workout_name

        for currSet in wo.sets:
            currStepIndex = currSet.stepIndex
            if currStepIndex is None:
                continue  # Ignores unscheduled exercises w/o stepIndex
            currSet.targetReps = garmin_data['steps'][currStepIndex]['durationValue']
            if currSet.exerciseName is None:
                newName = garmin_data['steps'][currStepIndex]['exerciseName']
                newCategory = garmin_data['steps'][currStepIndex]['exerciseCategory']
                currSet.exerciseName = newName if newName is not None else newCategory
    q.put(workouts)
    q.task_done()


def list_incomplete_workouts(workouts: list[Workout]):
    incomplete_workouts = []
    versionless_workouts = []

    for wo in workouts:
        wo.set_data_validation_check()
        if wo.isIncomplete or wo.name is None:
            incomplete_workouts.append(wo.datetime.split('T')[0])
        if wo.version is None:
            versionless_workouts.append(wo.datetime.split('T')[0])
    logger.info(f"Incomplete workouts: {incomplete_workouts}")
    logger.info(f"Version-less workouts: {versionless_workouts}")
