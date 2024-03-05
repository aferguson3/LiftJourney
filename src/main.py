import logging
from datetime import datetime, date, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from src import *
from src.models.Workout import Workout

DATA_FILEPATH = "./data/workout_data.json"
METADATA_FILEPATH = './data/workout_metadata.json'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


# TODO: investigate getting workouts from startDate onwards
# TODO: improve/review performance of adding targetReps funct
# TODO: changing exercise names is inconsistently saved


def list_available_exercises(dataframe: pd.DataFrame) -> list:
    values = dataframe['exerciseName'].drop_duplicates().values.tolist()
    if None in values:
        values.remove(None)
    values = sorted(values)
    return values


def load_dataframe(workouts: list[Workout]) -> pd.DataFrame:
    index_2d = []
    for workout in workouts:
        numSets = list(range(1, len(workout.sets) + 1))
        workoutDate = datetime.fromisoformat(workout.datetime).date().strftime("%m/%d/%y")
        for _set in numSets:
            index_2d.append((workoutDate, _set))
    setsData = view_sets_from_workouts(workouts)
    index_df = pd.MultiIndex.from_tuples(index_2d, names=["Dates", "Sets"])

    df = pd.DataFrame(setsData, index=index_df)
    df["date"] = [_date for (_date, s) in index_2d]
    return df


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


def set_params(weeks_of_workouts: int, limit: int, start: int, startDate: str | date):
    params = {
        "startDate": str(startDate),
        "endDate": date.fromisoformat(startDate) + timedelta(days=7 * weeks_of_workouts),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }
    return params


def user_exercise_selection(available_exercises: list) -> str:
    for index, exercise in enumerate(available_exercises):
        print(f"{index}: {exercise}")
    chosen_exercise = None
    while chosen_exercise is None:
        selection = input("Choose an exercise.")  # TODO: Secure input validation
        try:
            selection = int(selection)
            isInt = True
        except ValueError:
            selection = selection.upper()
            isInt = False

        if isInt and selection >= 0:
            try:
                chosen_exercise = available_exercises[selection]
            except IndexError:
                pass
        elif not isInt:
            chosen_exercise = selection if selection in available_exercises else None
        if chosen_exercise is None: print(f"Error: Invalid exercise: {selection}")

    return chosen_exercise


def main():
    client_auth()
    startDate = '2024-01-01'  # '2023-03-08'
    weeks_of_workouts = 5
    start = 0  #
    limit = 999  # max number of activities returned

    params = set_params(weeks_of_workouts, limit, start, startDate)

    metadata = {"numWorkouts": "", "filepath": METADATA_FILEPATH,
                "dates": {"firstWorkout": "", "lastWorkout": ""},
                }
    option = 2
    match option:
        case 1:  # Fresh data & backup
            IDs, dates = get_activities(params)
            workouts = get_workouts(IDs, dates)
            workouts_with_reps = fill_out_workouts(workouts)
            sorted_workouts = sort_workouts(workouts_with_reps, "datetime")
            dump_to_json(workouts_to_dict(sorted_workouts), DATA_FILEPATH, "w", metadata)
            list_incomplete_workouts(sorted_workouts)
        case 2:  # Fresh data & no backup
            IDs, dates = get_activities(params)
            workouts = get_workouts(IDs, dates)
            workouts_with_reps = fill_out_workouts(workouts)
            sorted_workouts = sort_workouts(workouts_with_reps, "datetime")
            list_incomplete_workouts(sorted_workouts)
        case _:  # Loaded data & no backup
            workouts = load_workouts(DATA_FILEPATH)
            sorted_workouts = sort_workouts(workouts, "datetime")
            list_incomplete_workouts(sorted_workouts)

    logger.info(
        f"Num of workouts: {len(sorted_workouts)}, Workout 0: {sorted_workouts[0].name} {sorted_workouts[0].version}"
        f"\nset 3: {sorted_workouts[0].view_sets()[3]}")

    df = load_dataframe(sorted_workouts)
    available_exercises = list_available_exercises(df)
    plotting_exercise = user_exercise_selection(available_exercises)

    plot_dataframe(df, plotting_exercise, 10)


if __name__ == "__main__":
    main()
