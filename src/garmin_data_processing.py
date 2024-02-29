import logging
from datetime import datetime, timedelta

import garth

from src.models import Workout, ExerciseSet
from src.utils import Endpoints

logger = logging.getLogger(__name__)


def get_activities(params: dict) -> (list, list):
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
    logger.info(
        f"Max limit for Ids: {params['limit']}, Number of Removed Ids: {len(removedIds)}, Number of Ids: {len(activityIds)}"
        f"\n{activityIds[:5]} ...")
    return activityIds, activityDatetimes


def get_workouts(activityIds: list, activityDatetimes: list) -> list[Workout]:
    totalWorkouts = list()  # most recent workouts stored first
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
                logger.info(f"Skipped {currSet['exercises'][0]['name']}, weight: {currSet['weight']}")
                continue
            currWeight = currSet["weight"] if currSet["weight"] is not None else 0
            curr_time_UTC_dt = datetime.fromisoformat(currSet["startTime"])
            EST = timedelta(hours=5)

            a_set.exerciseName = currSet["exercises"][0]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight = round(currWeight * 0.002204623)
            a_set.startTime = (curr_time_UTC_dt - EST).time().isoformat()
            a_set.stepIndex = currSet["wktStepIndex"]
            all_workout_sets.append(a_set)

        a_workout.activityId = Id
        a_workout.datetime = _datetime
        a_workout.sets = all_workout_sets
        totalWorkouts.append(a_workout)
    return totalWorkouts


def _isWarmupSet(garmin_exercise_set: dict) -> bool:
    result = garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BENCH_PRESS" and garmin_exercise_set[
        "weight"] <= 61251
    result = result or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BACK_SQUAT" and garmin_exercise_set[
        "weight"] <= 61251
    result = result or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_DEADLIFT" and garmin_exercise_set[
        "weight"] <= 61251
    return result
