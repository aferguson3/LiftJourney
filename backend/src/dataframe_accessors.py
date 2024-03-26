from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout


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
    setsData = Manager.view_sets_from_workouts(workouts)
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


def show_graph(sorted_workouts: list[Workout]):
    df = load_dataframe(sorted_workouts)
    available_exercises = list_available_exercises(df)
    exercise_to_plot = exercise_name_selection(available_exercises)
    available_target_reps = df.loc[(df["exerciseName"] == exercise_to_plot, "targetReps")].values
    target_reps = target_reps_selection(list(set(available_target_reps)))
    plot_dataframe(df, exercise_to_plot, target_reps)
