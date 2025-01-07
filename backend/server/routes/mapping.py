import logging

from flask import render_template, Blueprint, request
from sqlalchemy import select

from backend.server.config import db
from backend.server.database_interface import add_mappings, update_mappings
from backend.server.models import ExerciseSetDB
from backend.server.models.MuscleMapDB import MUSCLE_GROUPS_LIST, MuscleMapDB
from backend.server.models.forms import ExerciseMappingForm

logger = logging.getLogger(__name__)
mapping_bp = Blueprint("mapping_bp", __name__, url_prefix="")


def _format_display_exercise_names(values: list | str) -> list[str] | str:
    # applies title formatting when displayed on /caterpie
    if isinstance(values, list):
        values = [str(x).replace("_", " ").title() for x in values]
        if "None" in values:
            values.remove("None")
        values = sorted(values)
    elif isinstance(values, str):
        values = str(values).replace("_", " ").title()
    else:
        raise TypeError(f"Values must be a string or list but is {type(values)}")
    return values


def _format_DB_exercise_names(values: list | str) -> list[str] | str:
    # applies the single word & all caps formatting
    if isinstance(values, list):
        values = [str(x).replace(" ", "_").upper() for x in values]
        values = sorted(values)
    elif isinstance(values, str):
        values = str(values).replace(" ", "_").upper()
    else:
        raise TypeError(f"Values must be a string or list but is {type(values)}")
    return values


def initialize_muscle_map_db():
    exerciseSetDB_exercise_names = select(ExerciseSetDB.exerciseName).distinct()
    muscleMapDB_exercise_names = select(MuscleMapDB.exerciseName).distinct()
    new_muscleMapDB_exercise_names: list = (
        db.session.execute(
            exerciseSetDB_exercise_names.except_(muscleMapDB_exercise_names)
        )
        .scalars()
        .all()
    )
    try:
        new_muscleMapDB_exercise_names.remove(None)
    except ValueError:
        pass

    if len(new_muscleMapDB_exercise_names) > 0:
        muscle_map_collection = [
            MuscleMapDB(exerciseName=muscle_map, category="None")
            for muscle_map in new_muscleMapDB_exercise_names
        ]
        add_mappings(muscle_map_collection)


def _get_exercises_to_display():
    # noinspection PyTypeChecker
    result: list = (
        db.session.execute(
            select(MuscleMapDB.exerciseName).where(MuscleMapDB.category == "None")
        )
        .scalars()
        .all()
    )
    return _format_display_exercise_names(result)


@mapping_bp.route("/mapping", methods=["GET", "POST"])
def mapping():
    initialize_muscle_map_db()
    displayed_exercises = _get_exercises_to_display()
    muscle_group_field = ExerciseMappingForm()
    muscle_group_field.set_choices(MUSCLE_GROUPS_LIST)

    if request.method == "GET" or not muscle_group_field.is_submitted():
        return render_template(
            "exercise_mapping.html",
            exercises=displayed_exercises,
            muscle_group_field=muscle_group_field,
        )

    new_exercise_entries = list()
    submitted_form = request.form
    for cur_exercise_name in displayed_exercises:
        cur_selected_category = submitted_form.get(f"{cur_exercise_name}")

        if cur_selected_category != "":
            new_muscle_map = MuscleMapDB(
                exerciseName=_format_DB_exercise_names(cur_exercise_name),
                category=cur_selected_category,
            )
            new_exercise_entries.append(new_muscle_map)

    update_mappings(new_exercise_entries)
    new_displayed_exercises = _get_exercises_to_display()

    return render_template(
        "exercise_mapping.html",
        exercises=new_displayed_exercises,
        muscle_group_field=muscle_group_field,
    )
