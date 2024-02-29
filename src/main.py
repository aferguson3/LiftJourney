import logging
from datetime import datetime, date

import matplotlib.pyplot as plt
import pandas as pd

from src import *
from src.manage_workouts import list_incomplete_workouts
from src.models.Workout import Workout

DATA_FILEPATH = "./data/workout_data.json"
METADATA_FILEPATH = './data/workout_metadata.json'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


# TODO: investigate getting workouts from startDate onwards
# TODO: improve/review performance of adding targetReps funct
# TODO: changing exercise names is inconsistently saved


def main():
    client_auth()
    startDate = '2022-12-01'
    endDate = date.today().isoformat()
    start = 0  # modified by number of stored Workouts
    limit = 20  # max number of activities returned

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
    option = 1
    match option:
        case 1:
            IDs, dates = get_activities(params)
            workouts = get_workouts(IDs, dates)
            workouts_with_reps = fill_out_workouts(workouts)
            sorted_workouts = sort_workouts(workouts_with_reps, "datetime")
            dump_to_json(workouts_to_dict(sorted_workouts), DATA_FILEPATH, "w", metadata)
        case 2:
            IDs, dates = get_activities(params)
            workouts = get_workouts(IDs, dates)
            workouts_with_reps = fill_out_workouts(workouts)
            sorted_workouts = sort_workouts(workouts_with_reps, "datetime")
        case _:
            workouts = load_workouts(DATA_FILEPATH)
            sorted_workouts = sort_workouts(workouts, "datetime")
            list_incomplete_workouts(sorted_workouts)

    logger.info(
        f"Num of workouts: {len(sorted_workouts)}, Workout 0: {sorted_workouts[0].name} {sorted_workouts[0].version}"
        f"\nset 3: {sorted_workouts[0].view_sets()[3]}")

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
    plot_df.drop_duplicates(subset=["date"], inplace=True)  # Gets 1st rep of chosen exercise
    datapoints = len(plot_df)
    figsize = (datapoints, 6)

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
    df["date"] = [_date for (_date, s) in index_2d]
    return df


if __name__ == "__main__":
    main()
