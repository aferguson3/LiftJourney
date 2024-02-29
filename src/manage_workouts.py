import json
import logging
import re

import garth

from src.models.ExerciseSet import ExerciseSet
from src.models.Workout import Workout
from src.utils import Endpoints

logger = logging.getLogger(__name__)


def workouts_to_dict(data: list[Workout]) -> dict:
    if isinstance(data, list) is not True:
        raise TypeError(f"{data} is not type list.")

    workouts = list()
    for workout in data:
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

    if _metadata is not None:
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


def view_sets_from_workouts(workout_data: list[Workout]) -> dict:  # TODO: dynamic key allocation
    # Returns dict of all workouts sets
    if isinstance(workout_data, list) is not True:
        raise TypeError(f"{workout_data} is not type list.")

    _dict = {"duration_secs": [_set.duration_secs for wo in workout_data for _set in wo.sets],
             "exerciseName": [_set.exerciseName for wo in workout_data for _set in wo.sets],
             "numReps": [_set.numReps for wo in workout_data for _set in wo.sets],
             "targetReps": [_set.targetReps for wo in workout_data for _set in wo.sets],
             "startTime": [_set.startTime for wo in workout_data for _set in wo.sets],
             "stepIndex": [_set.stepIndex for wo in workout_data for _set in wo.sets],
             "weight": [_set.weight for wo in workout_data for _set in wo.sets]}

    return _dict


def fill_out_workouts(workouts: list[Workout]) -> list[Workout]:
    # Fills out targetReps and missing exerciseNames using scheduled workout info
    pattern = r"\b\d+(?:\.\d+)+\b"
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
                currSet.exerciseName = garmin_data['steps'][currStepIndex]['exerciseName']

    return workouts
