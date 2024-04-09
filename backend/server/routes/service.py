import logging
from datetime import datetime
from io import StringIO
from typing import Tuple

import pandas
import pandas as pd
from flask import Blueprint, request, render_template, session, url_for, redirect
from sqlalchemy import select, update

from backend.server import db
from backend.server.models import WorkoutDB, ExerciseSetDB
from backend.server.routes.database import new_DB_entries
from backend.src.dataframe_accessors import list_available_exercises, get_rep_ranges, plot_dataframe
from backend.src.garmin_interaction import run_service
from backend.src.utils import set_params_by_weeks

logger = logging.getLogger(__name__)
service_bp = Blueprint('service_bp', __name__, url_prefix='/main')


def _get_dataframe_index() -> list[Tuple]:
    index_2d: list[Tuple] = []
    workout_ids = db.session.execute(
        select(ExerciseSetDB.workout_id)
    ).scalars().unique().all()

    for cur_id in workout_ids:
        cur_workout_date = db.session.execute(
            select(WorkoutDB.datetime).where(WorkoutDB.id == int(cur_id))
        ).scalar()
        cur_sets = db.session.execute(
            select(ExerciseSetDB).where(ExerciseSetDB.workout_id == int(cur_id))
        ).all()

        cur_workout_date = datetime.fromisoformat(cur_workout_date).date().strftime("%m/%d/%y")
        set_numbers = list(range(1, len(cur_sets) + 1))
        for cur_set_number in set_numbers:
            index_2d.append((cur_workout_date, cur_set_number))
        db.session.execute(  # TODO: only update when empty
            update(ExerciseSetDB)
            .where(ExerciseSetDB.workout_id == int(cur_id))
            .values(date=cur_workout_date)
        )
        db.session.commit()
    return index_2d


def get_dataframe() -> pandas.DataFrame:
    sets_df = session.get('df')
    if sets_df is None:
        sets_df = pd.read_sql("exercise_sets", db.session.connection(), parse_dates={"startTime": "%H:%M:%S"})
        index_df = pd.MultiIndex.from_tuples(_get_dataframe_index(), names=["Dates", "Sets"])
        sets_df.set_index(index_df, inplace=True)
        session['df'] = sets_df.to_json()
    else:
        sets_df = pd.read_json(StringIO(sets_df))
    return sets_df


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
            session.pop('nextForm')
            reps = request.form['target-reps-select']
            session['reps'] = reps
            return redirect(url_for('.show_graph'))


@service_bp.route("/graph/show", methods=['GET'])
def show_graph():
    exercise = session['exercise']
    reps = session['reps'] if session['reps'] != "None" else None
    plot_src = plot_dataframe(get_dataframe(), exercise, reps, buffer_mode=True)
    return render_template("graph.html", plot_src=plot_src)
