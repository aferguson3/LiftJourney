import logging

from flask import Blueprint, request, render_template
from sqlalchemy import select

from backend.server import db
from backend.server.models import WorkoutDB

service_bp = Blueprint('service_bp', __name__, url_prefix='/main')


@service_bp.route("/run", methods=['GET'])
def service():
    args = request.args
    start_date = args.get("startDate", default="", type=str)  # provide start date or use the first date in DB
    weeks_of_workouts = args.get("weeks", default=10, type=int)

    if start_date == "":
        Result = db.session.execute(select(WorkoutDB.datetime).order_by(WorkoutDB.datetime.asc()))
        logging.info(f"{Result.first()}")
    return render_template("base.html", body=f"start: {start_date}, weeks: {weeks_of_workouts}")
