import logging
import multiprocessing
import pathlib
import queue
import re
import time
from datetime import datetime, timedelta
from threading import Thread

import garth
from dotenv import dotenv_values

from backend.src.models import Workout, ExerciseSet
from backend.src.utils import Endpoints

logger = logging.getLogger(__name__)
q = queue.Queue()
NUM_THREADS = 10 if multiprocessing.cpu_count() >= 10 else multiprocessing.cpu_count()


# Assumes Garmin connect user/pass are saved in .env file
def client_auth():
    working_dir = pathlib.Path.cwd().parent.parent
    creds_path = working_dir / "backend" / "creds"
    env_path = working_dir / ".env"
    try:
        garth.resume(str(creds_path))
        logger.info("0Auth tokens found. Login successful.")
    except FileNotFoundError:
        if not pathlib.Path.exists(creds_path):
            pathlib.Path.mkdir(creds_path)
        config = dotenv_values(str(env_path))
        garth.login(config["EMAIL"], config["PASSWORD"])
        garth.save(str(creds_path))


def get_activities(params: dict) -> (list[int], list[str]):
    # Gathers all fitness activities by date
    activity_data = garth.connectapi(f"{Endpoints.garmin_connect_activities}", params=params)
    activityIds, removedIds = list(), list()
    activityDatetimes = list()

    for activity in activity_data:
        if str(activity["activityName"]).find("Pickup") > -1 or str(activity["activityName"]).find("Basketball") > -1:
            # Excludes the basketball activities
            removedIds.append(activity["activityId"])
            continue

        activityIds.append(activity["activityId"])
        activityDatetimes.append(activity["startTimeLocal"])
    logger.debug(
        f"Max limit for Ids: {params['limit']}, Number of Removed Ids: {len(removedIds)}, Number of Ids: {len(activityIds)}"
        f"\n{activityIds[:5]} ...")
    return activityIds, activityDatetimes


def get_workouts(activityIds: list, activityDatetimes: list) -> list[Workout]:
    threads = []
    splice = int(len(activityIds) / NUM_THREADS)
    workouts_rv = []

    if len(activityIds) < NUM_THREADS:
        for ID, _datetime in zip(activityIds, activityDatetimes):
            t = Thread(target=_get_workouts_threaded, args=(activityDatetimes, ID))
            t.start()
            threads.append(t)
    else:
        for i in range(0, NUM_THREADS):
            cur_index = i * splice
            t = Thread(target=_get_workouts_threaded,
                       args=(
                           activityDatetimes[cur_index: cur_index + splice],
                           activityIds[cur_index: cur_index + splice]))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    while not q.empty():
        workouts_rv = workouts_rv + q.get()
    return workouts_rv


def _get_workouts_threaded(activityDatetimes: list, activityIds: list | int) -> None:
    totalWorkouts = list()  # most recent workouts stored first
    if isinstance(activityDatetimes, str):
        activityDatetimes = [activityDatetimes]
    if isinstance(activityIds, int):
        activityIds = [activityIds]

    for Id, _datetime in zip(activityIds, activityDatetimes):
        data = garth.connectapi(f"{Endpoints.garmin_connect_activity}/{Id}/exerciseSets")
        a_workout = Workout()
        all_workout_sets = list()

        for currSet in data["exerciseSets"]:
            a_set = ExerciseSet()
            if currSet["setType"] == "REST":
                continue
            if currSet["exercises"][0]["category"] == "INDOOR_BIKE":
                continue
            if _isWarmupSet(currSet):
                # skip warmup sets
                logger.debug(f"Skipped {currSet['exercises'][0]['name']}, weight: {currSet['weight']}")
                continue
            currWeight = currSet["weight"] if currSet["weight"] is not None else 0
            currTime = currSet["startTime"]
            curr_time_UTC_dt = datetime.fromisoformat(currTime) if currTime is not None else None
            EST = timedelta(hours=5)

            a_set.exerciseName = currSet["exercises"][0]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight = round(currWeight * 0.002204623)
            a_set.startTime = (curr_time_UTC_dt - EST).time().isoformat() if curr_time_UTC_dt is not None else None
            a_set.stepIndex = currSet["wktStepIndex"]
            all_workout_sets.append(a_set)

        a_workout.activityId = Id
        a_workout.datetime = _datetime
        a_workout.sets = all_workout_sets
        totalWorkouts.append(a_workout)
    q.put(totalWorkouts)
    q.task_done()


def _isWarmupSet(garmin_exercise_set: dict) -> bool:
    result = garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BENCH_PRESS" and garmin_exercise_set[
        "weight"] <= 61251
    result = result or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BACK_SQUAT" and garmin_exercise_set[
        "weight"] <= 61251
    result = result or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_DEADLIFT" and garmin_exercise_set[
        "weight"] <= 61251
    return result


def fill_out_workouts(workouts: list[Workout]) -> list[Workout]:
    # Fills out targetReps and missing exerciseNames using scheduled workout info
    start = time.perf_counter()
    threads = []
    splice = int(len(workouts) / NUM_THREADS)
    workouts_rv = []

    if len(workouts) < NUM_THREADS:
        for wo in workouts:
            t = Thread(target=_fill_out_workouts_threaded, args=[wo])
            t.start()
            threads.append(t)
    else:
        for i in range(0, NUM_THREADS):
            cur_index = i * splice
            t = Thread(target=_fill_out_workouts_threaded, args=[workouts[cur_index: cur_index + splice]])
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    while not q.empty():
        workouts_rv = workouts_rv + q.get()

    end = time.perf_counter()
    logger.info(f"{(end - start):.2f} seconds to fill out workouts")
    return workouts_rv


def _fill_out_workouts_threaded(workouts: list[Workout] | Workout):
    pattern = r"\b\d+(?:\.\d+)+\b"
    if isinstance(workouts, Workout):
        workouts = [workouts]

    for wo in workouts:
        garmin_data = garth.connectapi(f"{Endpoints.garmin_connect_activity}/{wo.activityId}/workouts")
        if garmin_data is None:
            print(f"{wo.datetime}")
            continue
        garmin_data = garmin_data[0]
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
            currSet.targetReps = int(garmin_data['steps'][currStepIndex]['durationValue'])
            if currSet.exerciseName is None:
                newName = garmin_data['steps'][currStepIndex]['exerciseName']
                newCategory = garmin_data['steps'][currStepIndex]['exerciseCategory']
                currSet.exerciseName = newName if newName is not None else newCategory
    q.put(workouts)
    q.task_done()
