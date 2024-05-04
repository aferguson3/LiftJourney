import logging
from datetime import datetime

from flask import Blueprint, request, render_template, session, redirect, url_for
from sqlalchemy import select

from backend.server import db
from backend.server.models import WorkoutDB
from backend.server.models.FormFields import ExerciseField, RepRangeField
from backend.server.routes.database import new_workout_entries
from backend.server.utils import get_dataframe
from backend.src.dataframe_accessors import (
    list_available_exercises,
    plot_dataframe,
    get_rep_ranges,
)
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks

logger = logging.getLogger(__name__)
service_bp = Blueprint("service_bp", __name__, url_prefix="/main")


# Uploads new workout entries
# URL Args: startDate (YYYY-MM-DD), weeks
@service_bp.route("/run", methods=["GET"])
def service():
    args = request.args
    start_date = args.get(
        "startDate", default=None, type=str
    )  # provide start date or use the first date in DB
    weeks_of_workouts = args.get("weeks", default=10, type=int)

    if start_date is None:
        result = (
            db.session.execute(
                select(WorkoutDB.datetime).order_by(WorkoutDB.datetime.desc())
            )
            .scalars()
            .first()
        )
        if result is None:  # no start date provided and empty DB
            logger.info(ValueError("DB is empty. Please select a start date."))
            return render_template(
                "base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}"
            )
        start_date = datetime.fromisoformat(result).date()
        logger.info(f"startDate: {start_date}, weeks: {weeks_of_workouts}")

    params = set_params_by_weeks(
        weeks_of_workouts=weeks_of_workouts, start_date=start_date
    )
    logger.info(params.items())
    workouts = run_service(params)
    new_workout_entries(workouts)
    return render_template(
        "base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}"
    )


@service_bp.route("/graph", methods=["GET", "POST"])
def setup_graph():
    df = get_dataframe()
    logger.info(f"df memory usage: {df.info(memory_usage=True)}")
    exercise_form = ExerciseField()
    reps_form = RepRangeField()
    all_exercises = list_available_exercises(df)
    # exercises_rep_ranges: dict[str, list[float]] = {x: get_rep_ranges(df, x) for x in all_exercises}
    exercise_form.set_choices(all_exercises)

    if request.method == "POST":
        if "exercises" in request.form:
            selected_exercise = exercise_form.exercises.data
            session["exercise"] = selected_exercise
            rep_ranges = get_rep_ranges(get_dataframe(), selected_exercise)
            reps_form.set_choices(rep_ranges)
            return render_template(
                "graph_params.html", exercise_form=exercise_form, reps_form=reps_form
            )

        elif "rep_ranges" in request.form:
            session["reps"] = reps_form.rep_ranges.data
            return redirect(url_for(".show_graph"))

    return render_template(
        "graph_params.html", exercise_form=exercise_form, reps_form=reps_form
    )


@service_bp.route("/graph/show", methods=["GET"])
def show_graph():
    exercise = session["exercise"]
    reps = float(session["reps"]) if session["reps"] != "None" else None
    plot_src = plot_dataframe(get_dataframe(), exercise, reps, buffer_mode=True)
    return render_template("graph.html", plot_src=plot_src)
