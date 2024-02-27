import logging
from datetime import datetime, date

import garth
import matplotlib.pyplot as plt
import pandas as pd

from src.auth import client_auth
from src.manage_workouts import sort_workouts, view_sets_from_workouts
from src.models.ExerciseSet import ExerciseSet
from src.models.Workout import Workout
from src.utils.Endpoints import Endpoints

DATA_FILEPATH = "./data/workout_data.json"
METADATA_FILEPATH = './data/workout_metadata.json'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


# TODO: investigate getting workouts from startDate onwards
# TODO: plotting data:
#           * show x tick for every day
#           * graph targetReps
# TODO: get target reps from /workouts
# TODO: make startTime for ES objs not a datetime value


def main():
    client_auth()
    startDate = '2023-01-01'
    endDate = date.today().isoformat()
    start = 0  # modified by number of stored Workouts
    limit = 42  # max number of activities returned

    params = {
        "startDate": str(startDate),
        "endDate": str(endDate),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }

    metadata = {"numWorkouts": "", "filepath": METADATA_FILEPATH,
                "dates": {"firstWorkout": "", "lastWorkout": ""},
                "start": start, "limit": limit
                }

    activityIds = get_activities(params)
    workouts = get_workouts(activityIds)
    logger.info(f"Num of workouts: {len(workouts)}, Workout 0 set 3: {workouts[0].view_sets()[3]}")

    sorted_workouts = sort_workouts(workouts, "datetime")
    # dump_to_json(workouts_to_dict(sorted_workouts), DATA_FILEPATH, "w", metadata)

    df = load_dataframe(sorted_workouts)

    # plot the reps and weight of like exercisesNames
    plotting_exercise = "BARBELL_BENCH_PRESS"
    plot_df = df.loc[df["exerciseName"] == plotting_exercise]
    plot_df.drop_duplicates(subset=["date"], inplace=True)  # Gets 1st rep of chosen exercise
    plot_df[["weight", "numReps"]].plot(subplots=True, kind='line', ylabel='Weight (lbs)', grid=True)
    plt.show()
    pass


def load_dataframe(workouts: list[Workout]) -> pd.DataFrame:
    index_2d = []
    for wo in workouts:
        numSets = list(range(1, len(wo.sets) + 1))
        workoutDate = datetime.fromisoformat(wo.datetime).date().strftime("%m/%d/%y")
        for _set in numSets:
            index_2d.append((workoutDate, _set))
    setsData = view_sets_from_workouts(workouts)
    index_df = pd.MultiIndex.from_tuples(index_2d, names=["Dates", "Sets"])

    df = pd.DataFrame(setsData, index=index_df)

    df["date"] = [d for (d, s) in index_2d]
    return df


def get_activities(params: dict):
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
    limit = params["limit"]
    logger.info(
        f"Max limit for Ids: {limit}, Number of Removed Ids: {len(removedIds)}, Number of Ids: {len(activityIds)}"
        f"\n{activityIds[:5]} ...")

    return activityIds


def get_workouts(activityIds):
    totalWorkouts = list()  # most recent workouts stored first
    for Id in activityIds:
        data = garth.connectapi(f"{Endpoints.garmin_connect_activity}/{Id}/exerciseSets")
        currWorkoutDate = None
        a_workout = Workout()
        all_workout_sets = list()

        for currSet in data["exerciseSets"]:
            a_set = ExerciseSet()
            if currWorkoutDate is None:
                currWorkoutDate = currSet["startTime"]
            if currSet["setType"] == "REST":
                continue
            if currSet["exercises"][0]["category"] == "INDOOR_BIKE":
                continue
            if ((currSet["exercises"][0]["name"] == "BARBELL_BENCH_PRESS" and currSet["weight"] <= 61251) or
                    (currSet["exercises"][0]["name"] == "BARBELL_BACK_SQUAT" and currSet["weight"] <= 61251)):
                # skip warmup sets
                logger.debug(f"Skipped {currSet['exercises'][0]['name']}, weight: {currSet['weight']}")
                continue
            currWeight = currSet["weight"]
            currWeight = currWeight if currWeight is not None else 0

            a_set.exerciseName = currSet["exercises"][0]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight = round(currWeight * 0.002204623)
            a_set.startTime = currSet["startTime"]
            a_set.stepIndex = currSet["wktStepIndex"]
            all_workout_sets.append(a_set)

        a_workout.activityId = Id
        a_workout.datetime = currWorkoutDate
        a_workout.sets = all_workout_sets
        totalWorkouts.append(a_workout)
    return totalWorkouts


if __name__ == "__main__":
    main()
