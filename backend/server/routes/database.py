import logging

from flask import Blueprint, render_template
from sqlalchemy import select

from backend.server import APP_DIRECTORY
from backend.server.config import db
from backend.server.database_interface import add_workouts
from backend.server.models.WorkoutDB import WorkoutDB, workoutsDB_to_dict
from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.utils import filepath_validation

# Unused routes: for debugging the SQLite db
logger = logging.getLogger(__name__)
database_bp = Blueprint("database_bp", __name__, url_prefix="/db")


def initialize_db():
    # purely initializing DB with stored workouts, NOT updating old entries
    app_directory = APP_DIRECTORY.parent
    datafile = app_directory.parent / "src" / "data" / "workout_data.json"
    load_db_from_file(datafile)

    return render_template("base.html", body="Done"), 200


def load_db_from_file(datafile: str):
    filepath_validation(datafile)
    workouts = Manager.load_workouts(str(datafile))
    add_workouts(workouts)


@database_bp.route("/workouts/<int:ID>")
def user_by_id(ID: int):
    result = db.get_or_404(WorkoutDB, ID)
    return render_template("base.html", body=f"{result}")


@database_bp.route("/all_workouts")
def full_db():
    workouts = db.session.execute(select(WorkoutDB)).scalars().all()
    workouts_dict = workoutsDB_to_dict(workouts)
    num_workouts = len(workouts_dict["workouts"])
    return render_template("base.html", body=f"# of workouts: {num_workouts}")
