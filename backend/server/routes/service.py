import io
import logging
from datetime import date

from flask import Blueprint, request, render_template, session, redirect, url_for, json

from backend.server.config import cache
from backend.server.database_interface import (
    add_workouts,
    select_mappings,
    select_activityIDs,
    select_datetimes,
)
from backend.server.models.MuscleMapDB import MuscleMapDB
from backend.server.models.forms import ExerciseMappingForm
from backend.server.routes.auth import login_check
from backend.server.routes.mapping import default_muscle_groupings
from backend.server.routes.status_codes import invalid_method
from backend.src.dataframe_accessors import (
    list_available_exercises,
    plot_dataframe,
)
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_date, set_params_by_weeks
from backend.src.utils.server_utils import get_sets_df, exercise_info_dict

logger = logging.getLogger(__name__)
service_bp = Blueprint(
    "service_bp",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder="static",
)


def _validate_dates(start_date: str, end_date: str) -> (str, str, str | None):
    error = None
    cur_date = start_date
    try:
        first_day = date.fromisoformat(cur_date)
        cur_date = end_date
        last_day = date.fromisoformat(cur_date)
        if first_day > last_day:
            error = f"Start Date: {str(first_day)} should occur before the End Date: {str(last_day)}"
            return "", "", error
    except ValueError:
        logger.info(f"Invalid iso format string: '{cur_date}'")
        error = "Invalid date(s). Select valid date(s)"
        return "", "", error

    return first_day, last_day, error


def _validate_weeks(weeks_arg: str) -> (int, str | None):
    error = None
    if weeks_arg.isdigit():
        result = int(weeks_arg)
    else:
        error = f"Invalid amount. Enter a valid number of weeks"
        return -1, error

    return result, error


# Uploads new workout entries
@service_bp.route("/retrieve-workouts", methods=["GET", "POST"])
def service():
    match request.method:
        case "GET":
            return retrieve_workouts_get()
        case "POST":
            return retrieve_workouts_post()
        case _:
            return invalid_method()


def retrieve_workouts_get():
    result = login_check()
    if result is not None:
        return result
    else:
        return render_template("retrieve_workouts.html")


def retrieve_workouts_post():
    selected_option = request.form.get("selection")

    match selected_option:
        case "dates":
            start_date, end_date, error = _validate_dates(
                request.form.get("start_date"), request.form.get("end_date")
            )
            if error is not None:
                return render_template("retrieve_workouts.html", error=error)
            params = set_params_by_date(start_date, end_date)

        case "weeks":
            weeks, error = _validate_weeks(request.form.get("weeks"))
            if error is not None:
                return render_template("retrieve_workouts.html", error=error)
            end_date = date.today()
            params = set_params_by_weeks(weeks, end_date)
        case _:
            logger.error(f"Option: {selected_option} not implemented.")
            error = "Try again."
            return render_template("retrieve_workouts.html", error=error)

    logger.info(params.items())
    stored_info = dict(zip(select_activityIDs(), select_datetimes()))
    workouts = run_service(params, stored_activity_info=stored_info)
    success = (
        f"Loaded workouts from {params.get("startDate")} to {params.get("endDate")}."
    )

    if workouts is not None:
        add_workouts(workouts)
        default_muscle_groupings()

    else:
        logger.info(f"No new workout entries.")
        success = "No new workouts were loaded."

    return render_template("retrieve_workouts.html", success=success)


@service_bp.route("/graph", methods=["GET", "POST"])
def graph_handler():
    match request.method:
        case "GET":
            return graph_get()
        case "POST":
            return graph_post()
        case _:
            return invalid_method()


def graph_get():
    df = get_sets_df()
    buffer = io.StringIO()
    df.info(memory_usage=True, buf=buffer)
    logger.info(f"df memory usage: {buffer.getvalue()}")
    fitness_select_form = ExerciseMappingForm()
    exercise_info = get_exercise_info(df)

    return render_template(
        "graph_params.html",
        muscle_group_field=fitness_select_form,
        exercise_info=json.dumps(exercise_info),
    )


@cache.cached(key_prefix="exercise_info")
def get_exercise_info(df):
    muscle_map_entries: list[MuscleMapDB] = select_mappings()
    all_muscle_maps = {
        _dict["exerciseName"]: _dict["category"]
        for _dict in [record.get_dict() for record in muscle_map_entries]
    }
    all_exercise_names = list_available_exercises(df)
    exercise_info = exercise_info_dict(all_exercise_names, df, all_muscle_maps)
    return exercise_info


def graph_post():
    fitness_select_form = ExerciseMappingForm()
    if fitness_select_form.is_submitted():
        if _validate_graph_args(request.form.to_dict()) == 0:
            session["exercise"] = request.form.get("exercises")
            session["reps"] = request.form.get("rep_ranges")
            return redirect(url_for(".show_graph"))

    df = get_sets_df()
    exercise_info = get_exercise_info(df)
    return render_template(
        "graph_params.html",
        muscle_group_field=fitness_select_form,
        exercise_info=json.dumps(exercise_info),
    )


def _validate_graph_args(form: dict) -> int:
    status = 0
    if (
        "categories" not in form.keys()
        or "exercises" not in form.keys()
        or "rep_ranges" not in form.keys()
    ):
        status = 1
    elif (
        form.get("categories") == ""
        or form.get("exercises") == ""
        or form.get("rep_ranges") == ""
    ):
        logger.debug("Submission prevented -- null graph param(s)")
        status = 2
    return status


@service_bp.route("/graph/show", methods=["GET"])
def show_graph():
    try:
        assert session["exercise"]
        assert session["reps"]
        assert session["exercise"] != ""
        assert session["reps"] != ""
    except KeyError or AssertionError:
        return (
            render_template(
                "base.html", body="400: Bad Request", title="400: Bad Request"
            ),
            400,
        )

    exercise = session["exercise"]
    reps_ = session["reps"]
    reps = int(reps_) if str(reps_).isdigit() else None
    plotly_div = plot_dataframe(
        get_sets_df(),
        exercise,
        reps,
        flask_mode=True,
    )
    return render_template(
        "graph_results.html",
        graph=plotly_div,
        exercise=str(exercise).replace("_", " ").title(),
    )
