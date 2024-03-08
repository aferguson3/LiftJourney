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
        plot_df = df.loc[df["exerciseName"] == plotting_exercise]
    else:
        plot_df = df.loc[(df["exerciseName"] == plotting_exercise) & (df["targetReps"] == targetReps)]

    fig, axes = plt.subplots(2, 1, sharex=True)
    axes[0].set_title(f"{plotting_exercise.replace('_', ' ').title()} Progress")
    plot_df = plot_df.drop_duplicates(subset=["date"], inplace=False)  # Gets 1st rep of chosen exercise
    datapoints = len(plot_df)
    figsize = (datapoints, 6)

    plot_df["weight"].plot(kind='line', ax=axes[0], ylabel='Weight (lbs)', grid=True)
    plot_df[["targetReps", "numReps"]].plot(kind='line', ax=axes[1], grid=True, xticks=range(datapoints),
                                            rot=30.0, figsize=figsize)
    plt.show()


def set_params_by_weeks(weeks_of_workouts: int, limit: int, start: int, startDate: str | date):
    params = {
        "startDate": str(startDate),
        "endDate": date.fromisoformat(startDate) + timedelta(days=7 * weeks_of_workouts),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }
    return params


def set_params_by_limit(limit: int, start: int, startDate: str | date = '2023-03-08'):
    params = {
        "startDate": str(startDate),
        "endDate": date.today(),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }
    return params


def exercise_name_selection(available_exercises: list) -> str:
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
    startDate = '2023-03-08'
    weeks_of_workouts = 15
    start = 0
    limit = 999  # max number of activities returned

    params = set_params_by_weeks(weeks_of_workouts, limit, start, startDate)
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
            params = set_params_by_weeks(10, limit, 0, '2023-12-01')

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
        f"\n\tset 3: {sorted_workouts[0].view_sets()[3]}")

    df = load_dataframe(sorted_workouts)
    available_exercises = list_available_exercises(df)
    exercise_to_plot = exercise_name_selection(available_exercises)
    available_target_reps = df.loc[(df["exerciseName"] == exercise_to_plot, "targetReps")].values
    available_target_reps = list(set(available_target_reps))
    target_reps = target_reps_selection(available_target_reps)

    plot_dataframe(df, exercise_to_plot, target_reps)


def target_reps_selection(available_target_reps: list) -> None | int:  # TODO: input validiation
    target_reps = None
    if len(available_target_reps) == 1:
        return None

    while target_reps is None:
        for rep_range in available_target_reps:
            print(f"{rep_range:.0f}, ", end="")
        print("or ENTER for no filter.")
        selection = input("Filter by target reps.")
        if selection == "":
            return None

        try:
            selection = int(selection)
        except ValueError:
            print(f"Invalid selection: {selection}")
            continue
        if selection in available_target_reps:
            target_reps = selection
            break
    return target_reps


if __name__ == "__main__":
    main()
