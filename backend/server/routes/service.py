import logging
from datetime import datetime

from flask import Blueprint, request, render_template
from sqlalchemy import select

from backend.server import db
from backend.server.models import WorkoutDB
from backend.server.routes.database import new_entries
from backend.src import get_activities, get_workouts, fill_out_workouts
from backend.src.WorkoutManagement import WorkoutManagement as Manager
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
        if result is None:
            logger.info(ValueError("DB is empty. Please select a start date."))
            return render_template("base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}")

        start_date = datetime.fromisoformat(result).date()
        logger.info(f"startDate: {start_date}, weeks: {weeks_of_workouts}")

    params = set_params_by_weeks(weeks_of_workouts=weeks_of_workouts, start_date=start_date)
    IDs, dates = get_activities(params)
    workouts = get_workouts(IDs, dates)
    workouts_with_reps = fill_out_workouts(workouts)
    Manager.list_incomplete_workouts(workouts_with_reps)

    new_entries(workouts_with_reps)
    return render_template("base.html", body=f"startDate: {start_date}, weeks: {weeks_of_workouts}")
