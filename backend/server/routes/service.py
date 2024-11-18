import io
import logging
import pathlib
import re
from datetime import datetime, date

from flask import Blueprint, request, render_template, session, redirect, url_for, json
from sqlalchemy import select

from backend.server.config import db
from backend.server.models import WorkoutDB
from backend.server.models.MuscleMapDB import MuscleMapDB
from backend.server.models.forms import ExerciseMappingForm
from backend.server.routes.database import new_workout_entries
from backend.server.utils import get_sets_df, get_exercise_info
from backend.src.dataframe_accessors import (
    list_available_exercises,
    plot_dataframe,
)
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks, timer

GRAPH_FILE = (
    pathlib.Path(__file__).parents[1] / "templates" / "DATA_exercise_graph.html"
)

logger = logging.getLogger(__name__)
service_bp = Blueprint(
    "service_bp",
    __name__,
    url_prefix="/main",
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


def get_start_date(start_date_arg: str | None) -> str | None:
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
@service_bp.route("/run", methods=["GET"])
@timer
def service():
    args = request.args
    weeks_of_workouts = args.get("weeks", default=10, type=int)
    start_date_arg = args.get("startDate")

    start_date = get_start_date(start_date_arg)
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

    workouts = run_service(params)
    if workouts is not None:
        new_workout_entries(workouts)
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
    muscle_map_entries: list[MuscleMapDB] = (
        (db.session.execute(select(MuscleMapDB))).scalars().all()
    )
    all_muscle_maps = {
        _dict["exerciseName"]: _dict["category"]
        for _dict in [record.get_dict() for record in muscle_map_entries]
    }
    all_exercise_names = list_available_exercises(df)
    exercise_info = get_exercise_info(all_exercise_names, df, all_muscle_maps)

    if fitness_select_form.is_submitted():
        if any(
            request.form.get(val) == ""
            for val in ["categories", "exercises", "rep_ranges"]
        ):
            logger.debug("Submission prevented -- null graph param(s)")
        else:
            session["exercise"] = request.form.get("exercises")
            session["reps"] = request.form.get("rep_ranges")
            return redirect(url_for(".show_graph"))

    return render_template(
        "graph_params.html",
        muscle_group_field=fitness_select_form,
        exercise_info=json.dumps(exercise_info),
    )


@service_bp.route("/graph/show", methods=["GET"])
def show_graph():
    exercise = session["exercise"]
    reps = float(session["reps"]) if session["reps"] != "None" else None
    plot_dataframe(
        get_sets_df(), exercise, reps, flask_mode=True, filepath=str(GRAPH_FILE)
    )
    return render_template(GRAPH_FILE.name)
