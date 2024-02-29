import logging
from datetime import datetime, date

import garth
import matplotlib.pyplot as plt
import pandas as pd

from src import *
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
# TODO: make startTime for ES objs not a datetime value
# TODO: improve/review performance of adding targetReps funct

def main():
    client_auth()
    startDate = '2022-12-01'
    endDate = date.today().isoformat()
    start = 0  # modified by number of stored Workouts
    limit = 40  # max number of activities returned

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
    option = 3
    match option:
        case 1:
            activityIds = get_activities(params)
            workouts = get_workouts(activityIds)
            workouts_with_reps = fill_out_workouts(workouts)
            sorted_workouts = sort_workouts(workouts_with_reps, "datetime")
            dump_to_json(workouts_to_dict(sorted_workouts), DATA_FILEPATH, "w", metadata)
        case 2:
            activityIds = get_activities(params)
            workouts = get_workouts(activityIds)
            workouts_with_reps = fill_out_workouts(workouts)
            sorted_workouts = sort_workouts(workouts_with_reps, "datetime")
        case _:
            workouts = load_workouts(DATA_FILEPATH)
            sorted_workouts = sort_workouts(workouts, "datetime")
    logger.info(f"Num of workouts: {len(sorted_workouts)}, Workout 0 set 3: {sorted_workouts[0].view_sets()[3]}")

    df = load_dataframe(sorted_workouts)
    plot_dataframe(df, "PULL_UP", 10)


def plot_dataframe(df, plotting_exercise: str, targetReps: int = None) -> None:
    # plot the reps and weight of like exercisesNames
    if plotting_exercise not in df['exerciseName'].values:
        raise ValueError(f"Exercise {plotting_exercise} is not in df")
    if targetReps is None:
        plot_df = df[(df["exerciseName"] == plotting_exercise)]
    else:
        plot_df = df[(df["exerciseName"] == plotting_exercise) & (df["targetReps"] == targetReps)]

    fig, axes = plt.subplots(2, 1, sharex=True)
    axes[0].set_title(f"{plotting_exercise.replace('_', ' ').title()} Progress")
    datapoints = len(plot_df)
    figsize = (datapoints, 6)

    plot_df.drop_duplicates(subset=["date"], inplace=True)  # Gets 1st rep of chosen exercise
    plot_df["weight"].plot(kind='line', ax=axes[0], ylabel='Weight (lbs)', grid=True)
    plot_df[["targetReps", "numReps"]].plot(kind='line', ax=axes[1], grid=True, xticks=range(datapoints),
                                            rot=30.0, figsize=figsize)
    plt.show()


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


def get_activities(params: dict) -> list:
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


def get_workouts(activityIds: list) -> list[Workout]:
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
            if _isWarmupSet(currSet):
                # skip warmup sets
                logger.info(f"Skipped {currSet['exercises'][0]['name']}, weight: {currSet['weight']}")
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


def _isWarmupSet(currSet) -> bool:
    result = currSet["exercises"][0]["name"] == "BARBELL_BENCH_PRESS" and currSet["weight"] <= 61251
    result = result or currSet["exercises"][0]["name"] == "BARBELL_BACK_SQUAT" and currSet["weight"] <= 61251
    result = result or currSet["exercises"][0]["name"] == "BARBELL_BACK_SQUAT" and currSet["weight"] <= 61251
    return result


if __name__ == "__main__":
    main()
