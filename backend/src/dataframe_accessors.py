import logging
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.server.models import Workout
from backend.src.WorkoutManagement import WorkoutManagement as Manager

logger = logging.getLogger(__name__)


def list_available_exercises(dataframe: pd.DataFrame) -> list:
    values = dataframe["exerciseName"].drop_duplicates().values.tolist()
    if None in values:
        values.remove(None)
    return sorted(values)


def load_dataframe(workouts: list[Workout]) -> pd.DataFrame:
    index_2d = []
    for workout in workouts:
        set_numbers = list(range(1, len(workout.sets) + 1))
        workoutDate = (
            datetime.fromisoformat(workout.datetime).date().strftime("%m/%d/%y")
        )
        for cur_set_number in set_numbers:
            index_2d.append((workoutDate, cur_set_number))
    setsData = Manager.view_sets_from_workouts(workouts)
    index_df = pd.MultiIndex.from_tuples(index_2d, names=["Dates", "Sets"])

    df = pd.DataFrame(setsData, index=index_df)
    df["date"] = [_date for (_date, s) in index_2d]
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    return df


def plot_dataframe(
    df: pd.DataFrame,
    plotting_exercise: str,
    targetReps: int = None,
    flask_mode: bool = False,
) -> None | str:
    # plot the reps and weight of like exercisesNames
    if plotting_exercise not in df["exerciseName"].values:
        raise ValueError(f"Exercise {plotting_exercise} is not in df")

    df["date_str"] = df["date"].dt.strftime("%m/%d/%y")
    df.sort_values(by=["date", "startTime"], inplace=True)
    df.drop_duplicates(
        subset=["date", "exerciseName"], inplace=True
    )  # Gets 1st rep of chosen exercise
    df = df.bfill()

    if targetReps is None:
        plot_df = df.loc[df["exerciseName"] == plotting_exercise]
    else:
        plot_df = df.loc[
            (df["exerciseName"] == plotting_exercise) & (df["targetReps"] == targetReps)
        ]
    fig = make_subplots(
        2, 1, shared_xaxes=True, vertical_spacing=0.025, horizontal_spacing=0.05
    )
    _setup_plot_formatting(plot_df, plotting_exercise, fig=fig)

    if not flask_mode:
        fig.show()
        return None

    config = {
        "responsive": True,
        "displayModeBar": "Hover",
        "doubleClickDelay": 350,
        "displaylogo": False,
        # "modeBarButtonsToAdd": "",
        "modeBarButtonsToRemove": ["toImage", "lasso", "select"],
    }
    graph_results = fig.to_html(
        config=config,
        include_plotlyjs="directory",
        div_id="plotly_graph",
        full_html=False,
    )
    return graph_results


def _setup_plot_formatting(
    plot_df: pd.DataFrame,
    plotting_exercise: str,
    fig=None,
) -> None:
    fig.add_trace(
        go.Scatter(
            x=plot_df["date_str"],
            y=plot_df["weight"],
            mode="lines+markers",
            name="Weight (lbs)",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=plot_df["date_str"],
            y=plot_df["targetReps"],
            mode="lines+markers",
            name="Target Reps",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=plot_df["date_str"],
            y=plot_df["numReps"],
            mode="lines+markers",
            name="Reps",
        ),
        row=2,
        col=1,
    )

    graph_title = f"{plotting_exercise.replace('_', ' ').title()} Progress"
    fig.update_layout(
        font={
            "family": "Arial, sans-serif",
            "size": 14,
            "textcase": "word caps",
            "weight": "normal",
        },
        title={
            "text": graph_title,
            "automargin": True,
            "font": {
                "size": 20,
                "textcase": "word caps",
                "weight": "normal",
            },
            "xref": "paper",
            "xanchor": "center",
            "yanchor": "top",
            "x": 0.5,
            "y": 0.975,
        },
        height=750,
        dragmode="pan",
        hovermode="x",
        hoversubplots="single",
        margin=dict(l=60, r=40, t=60, b=20),
        modebar={"orientation": "v"},
        xaxis2=dict(title="Dates"),
        yaxis=dict(title="Weight (lbs)"),
        yaxis2=dict(title="Target Reps vs Reps"),
        showlegend=False,
    )
    fig.update_xaxes(
        automargin="top+bottom",
        autorange=True,
    )
    fig.update_yaxes(title_standoff=3)


def exercise_name_selection(available_exercises: list) -> str:
    for index, exercise in enumerate(available_exercises):
        print(f"{index}: {exercise}")
    chosen_exercise = None
    while chosen_exercise is None:
        selection = input("Choose an exercise.")
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
        if chosen_exercise is None:
            print(f"Error: Invalid exercise: {selection}")

    return chosen_exercise


def target_reps_selection(available_target_reps: list) -> None | int:
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


def get_rep_ranges(df: pd.DataFrame, chosen_exercise: str) -> list[int]:
    target_reps = df.loc[
        (df["exerciseName"] == chosen_exercise, "targetReps")
    ].to_numpy(na_value=-1)
    target_reps = [int(item) for item in target_reps]
    target_reps = set(target_reps)

    if -1 in target_reps:
        target_reps.remove(-1)
    return sorted(target_reps)


def show_graph(sorted_workouts: list[Workout]):
    df = load_dataframe(sorted_workouts)
    available_exercises = list_available_exercises(df)
    exercise_to_plot = exercise_name_selection(available_exercises)
    rep_ranges = get_rep_ranges(df, exercise_to_plot)
    rep_range_selected = target_reps_selection(rep_ranges)
    plot_dataframe(df, exercise_to_plot, rep_range_selected)
