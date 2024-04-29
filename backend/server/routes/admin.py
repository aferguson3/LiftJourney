import logging

from flask import render_template, Blueprint
from sqlalchemy import select

from backend.server import db
from backend.server.models import ExerciseSetDB
from backend.server.models.FormFields import CategoryField

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin_bp', __name__, url_prefix="/admin")


# obfuscate admin routes w/ pokemon
# clear: clefairy
# set categories: caterpie
@admin_bp.route("/clefairy")
def clear_db():
    db.drop_all()
    return render_template('base.html', body="Empty")


@admin_bp.route("/caterpie", methods=['GET', 'POST'])
def set_categories():
    def _format_exercises(values: list) -> list[str]:
        values = [str(x).replace("_", " ").title() for x in values]
        if "None" in values:
            values.remove("None")
        return sorted(values)

    categories = ["Arms", "Chest", "Core", "Back", "Legs", "Shoulders"]
    all_exercises = (
        db.session.execute(select(ExerciseSetDB.exerciseName))
    ).scalars().unique().all()
    all_exercises = _format_exercises(all_exercises)
    # check with saved exercise categories; removed saved exercise names for this list
    categories_field = CategoryField()
    categories_field.set_choices(categories)
    # On submit, check for invalid category selections
    if categories_field.is_submitted():
        raise ValueError
    return render_template('set_exercise_categories.html', all_exercises=all_exercises,
                           categories_field=categories_field)
