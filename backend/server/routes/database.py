import logging
import os

from flask import Blueprint, render_template
from sqlalchemy import select

from backend.server import db
from backend.server.models.WorkoutDB import WorkoutDB, workoutsDB_to_dict
from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout

logger = logging.getLogger(__name__)
database_bp = Blueprint('database_bp', __name__, url_prefix="/db")


def isNewWorkoutEntry(entry: WorkoutDB) -> bool:
    result = db.session.execute(
        select(WorkoutDB.activityId).where(WorkoutDB.activityId == int(entry.activityId))
    ).scalars().first()
    return result is None


def new_DB_entries(workouts: list[Workout]):
    if not isinstance(workouts[0], Workout):
        raise ValueError(f"{type(workouts[0])} is not type Workout")

    workoutsDB = WorkoutDB.convert_to_workoutsDB(workouts)
    for wo in workoutsDB:
        if not isNewWorkoutEntry(wo):
            continue
        db.session.add(wo)
    db.session.commit()


@database_bp.route("/load/from_file")
def initialize_db():
    # purely initializing DB with stored workouts, NOT updating old entries
    DATAFILE_REL = r"..\src\data\workout_data.json"
    DATAFILE_ABS = os.path.normpath(os.path.join(os.getcwd(), DATAFILE_REL))
    workouts = Manager.load_workouts(DATAFILE_ABS)
    new_DB_entries(workouts)

    return render_template("base.html", body="Done"), 200


@database_bp.route("/workouts/<int:ID>")
def user_by_id(ID):
    result = db.get_or_404(WorkoutDB, ID)
    return render_template('base.html', body=f"{result}")


@database_bp.route("/all_workouts")
def full_db():
    workouts = db.session.execute(select(WorkoutDB)).scalars().all()
    workouts_dict = workoutsDB_to_dict(workouts)
    return render_template('base.html', body=f"# of workouts: {len(workouts_dict["workouts"])}")


@database_bp.route("/clear_db")
def clear_db():
    db.drop_all()
    return render_template('base.html', body="Empty")
