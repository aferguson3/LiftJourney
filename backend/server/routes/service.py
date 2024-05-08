import io
import logging
from datetime import datetime

from flask import (
    Blueprint,
    request,
    render_template,
    session,
    redirect,
    url_for,
)
from sqlalchemy import select

from backend.server import db
from backend.server.models import WorkoutDB
from backend.server.models.ExerciseDB import ExerciseDB
from backend.server.models.FormFields import ExerciseField, CategoryField
from backend.server.routes.database import new_workout_entries
from backend.server.utils import get_dataframe
from backend.server.utils.utils import get_exercise_info
from backend.src.dataframe_accessors import (
    list_available_exercises,
    plot_dataframe,
)
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks
from backend.src.utils import timer

logger = logging.getLogger(__name__)
service_bp = Blueprint("service_bp", __name__, url_prefix="/main")


# Uploads new workout entries
# URL Args: startDate (YYYY-MM-DD), weeks
@service_bp.route("/run", methods=["GET"])
@timer
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
    if workouts is not None:
        new_workout_entries(workouts)
    else:
        logger.info(f"No new workout entries.")

    return render_template(
        "base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}"
    )


@service_bp.route("/graph", methods=["GET", "POST"])
def setup_graph():
    df = get_dataframe()
    buffer = io.StringIO()
    df.info(memory_usage=True, buf=buffer)
    logger.info(f"df memory usage: {buffer.getvalue()}")

    exercise_field = ExerciseField()
    if exercise_field.is_submitted():
        session["exercise"] = request.form.get("exercises")
        session["reps"] = request.form.get("rep_ranges")
        return redirect(url_for(".show_graph"))

    categorized_exercises: list[ExerciseDB] = (
        (db.session.execute(select(ExerciseDB))).scalars().all()
    )
    categories_field = CategoryField()
    exercises_categories = {
        _dict["exerciseName"]: _dict["category"]
        for _dict in [_exerciseDB.get_dict() for _exerciseDB in categorized_exercises]
    }
    all_exercises = list_available_exercises(df)
    exercise_info = get_exercise_info(all_exercises, df, exercises_categories)
    exercise_field.set_choices(all_exercises)

    return render_template(
        "graph_params.html",
        categories_field=categories_field,
        exercise_info=exercise_info,
    )


@service_bp.route("/graph/show", methods=["GET"])
def show_graph():
    exercise = session["exercise"]
    reps = float(session["reps"]) if session["reps"] != "None" else None
    plot_src = plot_dataframe(get_dataframe(), exercise, reps, buffer_mode=True)
    return render_template("graph.html", plot_src=plot_src)
