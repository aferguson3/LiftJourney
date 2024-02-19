import logging
import garth
import pandas as pd
import numpy as np
import xarray as xr

from datetime import date
from src.auth import client_auth
from utils.Endpoints import Endpoints
from utils.Workout import ExerciseSet, Workout

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def main():
    client_auth()
    startDate = '2023-01-01'  # future startDate gotten from stored data
    endDate = date.today().isoformat()
    limit = 10

    params = {
        "startDate": str(startDate),
        "endDate": str(endDate),
        "start": 0,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }
    # Gathers all fitness activities by date
    activity_data = garth.connectapi(f"{Endpoints.garmin_connect_activities}", params=params)
    activityIds, removedIds = list(), list()
    # Gathers collected activityIDs but excludes the basketball events
    for activity in activity_data:
        if (activity["activityName"] == "Pickup" or activity["activityName"] == "Basketball Workout" or
                activity["activityName"] == "Basketball"):
            removedIds.append(activity["activityId"])
            continue
        activityIds.append(activity["activityId"])
    logger.info(
        f"Max limit for Ids: {limit}, Number of Removed Ids: {len(removedIds)}, Number of Ids: {len(activityIds)}\n{activityIds[:5]} ...")

    totalWorkouts = list()  # most recent workouts stored first
    for Id in activityIds:
        data = garth.connectapi(f"{Endpoints.garmin_connect_activity}/{Id}/exerciseSets")
        currWorkoutDate = None
        a_workout = Workout()
        all_workout_sets = list()

        for currSet in data["exerciseSets"]:
            a_set = ExerciseSet()  # same set = name + same stepIndex
            if currSet["setType"] == "REST":
                continue
            if currSet["exercises"][0]["category"] == "INDOOR_BIKE" and currWorkoutDate is None:
                currWorkoutDate = currSet["startTime"]
                continue
            a_set.exerciseName = currSet["exercises"][0]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight_grams = currSet["weight"]
            a_set.startTime = currSet["startTime"]
            a_set.stepIndex = currSet["wktStepIndex"]
            all_workout_sets.append(a_set)

        a_workout.activityId = Id
        a_workout.datetime = currWorkoutDate
        a_workout.sets = all_workout_sets
        totalWorkouts.append(a_workout)

        logger.info(f"Workout data: datetime: {a_workout.datetime} Num of sets: {len(a_workout.sets)}")
        logger.info(f"Num of workouts: {len(totalWorkouts)} activityID: {a_workout.activityId}")


if __name__ == "__main__":
    main()
