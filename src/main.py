import dataclasses
import json
import logging
from datetime import date

import garth
import xarray as xr

from src.auth import client_auth
from utils.Endpoints import Endpoints
from utils.Workout import ExerciseSet, Workout

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def workouts_to_dict(data: list[Workout]) -> dict:
    _list = [w.asdict() for w in data]
    _dict = {"workouts": _list}
    return _dict


def dump_data(data: list | dict, filepath: str, option="a"):
    data_dict = data
    if data is list:
        data_dict = workouts_to_dict(data)
    match option:
        case "a" | "w":
            try:
                with open(filepath, option) as file:
                    json.dump(data_dict, file, sort_keys=True)
            except FileNotFoundError as e:
                print(f"{filepath} not found.")
        case _:
            return -1


def load_data(filepath: str) -> list:
    try:
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            json_data = json_data["workouts"]
            all_workouts = list()
            for workout in json_data:
                a_workout = Workout()
                a_workout.load(workout)
                all_workouts.append(a_workout)
        return all_workouts

    except FileNotFoundError as e:
        print(f"{filepath} not found.")


def transverse_by_set_label(label: str, workouts: dict | list) -> None:
    # transverse workouts by given dict key
    allWorkouts = workouts
    matchedList = list()
    if workouts is list:
        allWorkouts = workouts_to_dict(workouts)

    for (key, value) in allWorkouts.items():
        if label in allWorkouts["1"]:
            pass

    return None


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
            a_set = ExerciseSet()
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
        # logger.info(f"Workout data: datetime: {a_workout.datetime} Num of sets: {len(a_workout.sets)}

    logger.info(f"Num of workouts: {len(totalWorkouts)}, Workout 0 set 3: {totalWorkouts[0].view_sets()[3]}")
    filepath = "../data/workout_data.json"
    # for workout in totalWorkouts:
    #     workout.validation_check()
    # dump_data(totalWorkouts, filepath)

    workout_dict = workouts_to_dict(totalWorkouts)
    time_dims = [v["datetime"] for (k, v) in workout_dict.items()]
    sets_dims = [len(v["sets"]) for (k, v) in workout_dict.items()]

    ds = xr.Dataset(data_vars={
        "duration": (("datetime", "sets"),),
        "name": "",
        "reps": "",
        "weight": "",
        "stepIndex": ""
    }, coords={
        "datetime": time_dims,
        "sets": sets_dims
    })


if __name__ == "__main__":
    main()
# TODO: reverse order workouts in json file
# TODO: get target reps from /workouts
