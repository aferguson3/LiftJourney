import logging
from datetime import datetime

from flask import Blueprint, request, render_template, session, url_for, redirect
from sqlalchemy import select

from backend.server import db
from backend.server.models import WorkoutDB
from backend.server.routes.database import new_DB_entries
from backend.server.utils import remove_from_session, get_dataframe
from backend.src.dataframe_accessors import list_available_exercises, get_rep_ranges, plot_dataframe
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks

logger = logging.getLogger(__name__)
service_bp = Blueprint('service_bp', __name__, url_prefix='/main')


# Uploads new workout entries
# URL Args: startDate, weeks
@service_bp.route("/run", methods=['GET'])
def service():
    args = request.args
    start_date = args.get("startDate", default="", type=str)  # provide start date or use the first date in DB
    weeks_of_workouts = args.get("weeks", default=10, type=int)

    if start_date == "":
        result = db.session.execute(
            select(WorkoutDB.datetime).order_by(WorkoutDB.datetime.desc())
        ).scalars().first()
        if result is None:  # no start date provided and empty DB
            logger.info(ValueError("DB is empty. Please select a start date."))
            return render_template("base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}")
        start_date = datetime.fromisoformat(result).date()
        logger.info(f"startDate: {start_date}, weeks: {weeks_of_workouts}")

    params = set_params_by_weeks(weeks_of_workouts=weeks_of_workouts, start_date=start_date)
    workouts = run_service(params)
    new_DB_entries(workouts)
    return render_template("base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}")


@service_bp.route("/graph", methods=['GET', 'POST'])
def setup_graph():
    if request.method == 'GET':
        remove_from_session('df')
        df = get_dataframe()
        logger.info(f"df memory usage: {df.info(memory_usage=True)}")
        session['nextForm'] = 'exercise_selection'
        return render_template("exercise_selection.html", exercises=list_available_exercises(df))

    elif request.method == 'POST':
        req_form_name = session['nextForm']
        if req_form_name == "exercise_selection":
            exercise = request.form['exercise-select']
            session['exercise'] = exercise
            session['nextForm'] = "target_reps_selection"
            rep_ranges = get_rep_ranges(get_dataframe(), exercise)
            return render_template('target_reps_selection.html', target_reps=rep_ranges)

        elif req_form_name == "target_reps_selection":
            remove_from_session('nextForm')
            reps = request.form['target-reps-select']
            session['reps'] = reps
            return redirect(url_for('.show_graph'))


@service_bp.route("/graph/show", methods=['GET'])
def show_graph():
    exercise = session['exercise']
    reps = session['reps'] if session['reps'] != "None" else None
    plot_src = plot_dataframe(get_dataframe(), exercise, reps, buffer_mode=True)
    return render_template("graph.html", plot_src=plot_src)
