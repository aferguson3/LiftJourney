import json
import logging
from datetime import date

import garth

from src.auth import client_auth
from src.utils.Endpoints import Endpoints
from src.models.Workout import Workout
from src.models.ExerciseSet import ExerciseSet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def workouts_to_dict(data: list[Workout]) -> dict:
    workouts = list()
    for workout in data:
        workout.validation_check()
        workouts.append(workout.asdict())
    return {"workouts": workouts}


def dump_data(data: dict, filepath: str, option):
    match option:
        case "a" | "w":
            try:
                with open(filepath, option) as file:
                    json.dump(data, file, sort_keys=True)
            except FileNotFoundError as e:
                print(f"{filepath} not found.")
            except TypeError as e:
                print(f"{e} Check data's type.")
        case _:
            raise ValueError(f"Invalid option:{option} used in json.dump().")


def load_data(filepath: str) -> list[Workout]:
    try:
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            all_workouts = list()
            for workout in json_data["workouts"]:
                a_workout = Workout()
                a_workout.load(workout)
                all_workouts.append(a_workout)
        return all_workouts

    except FileNotFoundError as e:
        print(f"{e}")


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
    # filepath = "../data/workout_data.json"
    # dump_data(workouts_to_dict(totalWorkouts), filepath, "w")

    # workout_dict = workouts_to_dict(totalWorkouts)["workouts"]
    # xr


if __name__ == "__main__":
    main()
# TODO: reverse order workouts in json file
# TODO: get target reps from /workouts
# TODO: plotting sets data
# TODO: implement testing
