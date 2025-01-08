import io
import logging
import re
from datetime import datetime, date

from flask import Blueprint, request, render_template, session, redirect, url_for, json
from sqlalchemy import select

from backend.server.config import db, cache
from backend.server.database_interface import (
    add_workouts,
    select_mappings,
    select_activityIDs,
    select_datetimes,
)
from backend.server.models import WorkoutDB
from backend.server.models.MuscleMapDB import MuscleMapDB
from backend.server.models.forms import ExerciseMappingForm
from backend.src.dataframe_accessors import (
    list_available_exercises,
    plot_dataframe,
)
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks
from backend.src.utils.server_utils import get_sets_df, get_exercise_info

logger = logging.getLogger(__name__)
service_bp = Blueprint(
    "service_bp",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder="static",
)


def _validate_start_date(start_date_arg: str) -> str:
    VALID_ISOFORMAT = r"\d{4}[-]\d{2}[-]\d{2}"
    today = date.today()
    match = re.search(VALID_ISOFORMAT, str(start_date_arg))

    if match is None:
        logger.info(f"No valid iso format strings: '{start_date_arg}'")
        return "ERROR: NO-MATCH"

    _date_match = match.group(0)
    try:
        start_date: date = date.fromisoformat(_date_match)
        if start_date > today:
            logger.debug(f"{start_date} is in the future.")
            start_date = today
        return str(start_date)
    except ValueError as e:
        logger.debug(e)
        return "ERROR: INVALID"


def _get_start_date(start_date_arg: str | None) -> str | None:
    if start_date_arg is None:
        pass

    result = _validate_start_date(start_date_arg)
    if result.find("ERROR") == -1:
        return result

    last_stored_workout_date = (
        db.session.execute(
            select(WorkoutDB.datetime).order_by(WorkoutDB.datetime.desc())
        )
        .scalars()
        .first()
    )
    if last_stored_workout_date is None:
        # no start date provided and empty DB
        logger.info(ValueError("DB is empty. Please select a start date."))
        return

    return str(datetime.fromisoformat(last_stored_workout_date).date())


# Uploads new workout entries
# URL Args: startDate (YYYY-MM-DD), weeks
@service_bp.route("/retrieve-workouts", methods=["GET"])
def service():
    args = request.args
    weeks_of_workouts = args.get("weeks", default=10, type=int)
    start_date_arg = args.get("startDate")

    start_date = _get_start_date(start_date_arg)
    if start_date is None:  # empty DB case
        return render_template(
            "base.html",
            body=f"startDate: {start_date}, weeks: {weeks_of_workouts}",
        )

    logger.info(f"startDate: {start_date}, weeks: {weeks_of_workouts}")
    params = set_params_by_weeks(
        weeks_of_workouts=weeks_of_workouts, start_date=start_date
    )
    logger.info(params.items())

    stored_info = dict(zip(select_activityIDs(), select_datetimes()))
    workouts = run_service(params, stored_activity_info=stored_info)
    if workouts is not None:
        add_workouts(workouts)
    else:
        logger.info(f"No new workout entries.")

    return render_template(
        "base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}"
    )


@service_bp.route("/graph", methods=["GET", "POST"])
def setup_graph():
    df = get_sets_df()
    buffer = io.StringIO()
    df.info(memory_usage=True, buf=buffer)
    logger.info(f"df memory usage: {buffer.getvalue()}")

    fitness_select_form = ExerciseMappingForm()
    if cache.get("exercise_info") is None:
        muscle_map_entries: list[MuscleMapDB] = select_mappings()
        all_muscle_maps = {
            _dict["exerciseName"]: _dict["category"]
            for _dict in [record.get_dict() for record in muscle_map_entries]
        }
        all_exercise_names = list_available_exercises(df)
        exercise_info = get_exercise_info(all_exercise_names, df, all_muscle_maps)
    else:
        exercise_info = cache.get("exercise_info")
        logging.debug("Cache used for key: exercise_info")

    if fitness_select_form.is_submitted():
        if _validate_args(request.form.to_dict()) == 0:
            session["exercise"] = request.form.get("exercises")
            session["reps"] = request.form.get("rep_ranges")
            return redirect(url_for(".show_graph"))

    return render_template(
        "graph_params.html",
        muscle_group_field=fitness_select_form,
        exercise_info=json.dumps(exercise_info),
    )


def _validate_args(form: dict) -> int:
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
