import logging

from flask import render_template, Blueprint, request
from sqlalchemy import select

from backend.server.config import db
from backend.server.database_interface import add_mappings, update_mappings
from backend.server.models import ExerciseSetDB
from backend.server.models.MuscleMapDB import MUSCLE_GROUPS_LIST, MuscleMapDB
from backend.server.models.forms import ExerciseMappingForm
from backend.server.routes.status_codes import invalid_method

logger = logging.getLogger(__name__)
mapping_bp = Blueprint("mapping_bp", __name__, url_prefix="")


def _display_name_formatting(values: list | str) -> list[str] | str:
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


def _database_name_formatting(values: list | str) -> list[str] | str:
    # applies the single word & all caps formatting
    if isinstance(values, list):
        values = [str(x).replace(" ", "_").upper() for x in values]
        values = sorted(values)
    elif isinstance(values, str):
        values = str(values).replace(" ", "_").upper()
    else:
        raise TypeError(f"Values must be a string or list but is {type(values)}")
    return values


def _change_exercise_mappings(exercise_names: list, categories: list) -> dict | None:
    changes_to_db = False
    # noinspection PyTypeChecker
    db_mappings = db.session.execute(
        select(MuscleMapDB.exerciseName, MuscleMapDB.category).where(
            MuscleMapDB.category != "None"
        )
    ).all()
    db_mappings = dict(db_mappings)
    for row in zip(exercise_names, categories, strict=True):
        cur_exercise = row[0]
        cur_category = row[1]
        if db_mappings.get(cur_exercise) is None:
            continue
        if db_mappings[cur_exercise] == cur_category:
            db_mappings.pop(cur_exercise)
        else:
            changes_to_db = True
            db_mappings[cur_exercise] = cur_category

    if changes_to_db:
        update_mappings(db_mappings)
        return db_mappings
    else:
        logger.debug("No new muscle mappings to update.")
        return None


def _default_muscle_groupings():
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


def load_ungrouped_exercises():
    # noinspection PyTypeChecker
    result: list = (
        db.session.execute(
            select(MuscleMapDB.exerciseName).where(MuscleMapDB.category == "None")
        )
        .scalars()
        .all()
    )
    return _display_name_formatting(result)


def load_muscle_mappings() -> tuple[list, list]:
    exercise_names, categories = list(), list()
    # noinspection PyTypeChecker

    result: list = db.session.execute(
        select(MuscleMapDB.exerciseName, MuscleMapDB.category).where(
            MuscleMapDB.category != "None"
        )
    ).all()
    for row in result:
        exercise_names.append(row[0])
        categories.append(row[1])
    return _display_name_formatting(exercise_names), categories


@mapping_bp.route("/mapping", methods=["GET", "POST"])
def mapping():
    match request.method:
        case "GET":
            return mapping_get()
        case "POST":
            return mapping_post_handler()
        case _:
            return invalid_method()


def mapping_get():
    muscle_group_field = ExerciseMappingForm()
    return render_template(
        "exercise_mapping.html",
        muscle_group_field=muscle_group_field,
        exercises=None,
    )


@mapping_bp.route("/mapping/menu_change", methods=["POST"])
def menu_selection():
    option = request.form.get("menu_select")
    muscle_group_field = ExerciseMappingForm()

    match option:
        case "modify":
            current_exercises, categories = load_muscle_mappings()
            exercise_categories = list(zip(current_exercises, categories))
            return render_template(
                "exercise_mapping.html",
                exercises=current_exercises,
                exercise_categories=exercise_categories,
                muscle_group_field=muscle_group_field,
            )
        case "create":
            _default_muscle_groupings()
            displayed_exercises = load_ungrouped_exercises()

            return render_template(
                "exercise_mapping.html",
                exercises=displayed_exercises,
                muscle_group_field=muscle_group_field,
            )
        case _:
            logger.error("Invalid menu options")
            return render_template(
                "exercise_mapping.html",
                exercises=None,
                muscle_group_field=muscle_group_field,
                error="400: Invalid menu option",
            )


@mapping_bp.route("/mapping/submission_change", methods=["POST"])
def mapping_post_handler():
    option = request.form.get("menu_select")
    match option:
        case "modify":
            return modifying_mappings()
        case "create":
            return creating_mappings()
        case _:
            return invalid_method()


def modifying_mappings() -> str:
    muscle_group_field = ExerciseMappingForm()
    request_form = request.form.copy()
    valid_categories = MUSCLE_GROUPS_LIST.copy()
    valid_categories.append("None")
    updated_entries = dict()

    cur_exercises, cur_categories = load_muscle_mappings()
    for exercise_name, stored_category in zip(cur_exercises, cur_categories):
        updated_category = request_form.get(exercise_name)
        if stored_category not in valid_categories:
            logger.debug(
                f"Invalid mapping: {exercise_name}:{stored_category}. Use valid categories."
            )
            continue
        if updated_category != stored_category:
            updated_entries[_database_name_formatting(exercise_name)] = updated_category

    _change_exercise_mappings(
        list(updated_entries.keys()), list(updated_entries.values())
    )
    cur_exercises, cur_categories = load_muscle_mappings()
    exercise_categories = list(zip(cur_exercises, cur_categories))
    return render_template(
        "exercise_mapping.html",
        exercises=cur_exercises,
        exercise_categories=exercise_categories,
        muscle_group_field=muscle_group_field,
    )


def creating_mappings() -> str:
    # mapping process submitted form
    new_exercise_entries = list()
    displayed_exercises = load_ungrouped_exercises()
    muscle_group_field = ExerciseMappingForm()
    submitted_form = request.form

    for cur_exercise_name in displayed_exercises:
        cur_selected_category = submitted_form.get(f"{cur_exercise_name}")
        if cur_selected_category != "None":
            new_muscle_map = MuscleMapDB(
                exerciseName=_database_name_formatting(cur_exercise_name),
                category=cur_selected_category,
            )
            new_exercise_entries.append(new_muscle_map)

    if len(new_exercise_entries) > 0:
        update_mappings(new_exercise_entries)
        displayed_exercises = load_ungrouped_exercises()
    else:
        logger.debug("No new muscle mappings to add.")

    return render_template(
        "exercise_mapping.html",
        exercises=displayed_exercises,
        muscle_group_field=muscle_group_field,
    )
