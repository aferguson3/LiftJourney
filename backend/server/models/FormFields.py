from flask_wtf import FlaskForm
from wtforms import SelectField

from backend.server.models.ExerciseDB import CATEGORY_LIST


def _pretty_str(name: str):
    return name.replace("_", " ")


class CategoryField(FlaskForm):
    categories = SelectField("Categories")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_choices(CATEGORY_LIST)

    def set_choices(self, options: list[str]):
        self.categories.choices = [("", "-- Select a Category --")] + [
            (name, _pretty_str(name)) for name in options
        ]


class ExerciseField(FlaskForm):
    exercises = SelectField("Exercises")

    def set_choices(self, options: list[str]):
        self.exercises.choices = [("", "-- Select an Exercise --")] + [
            (name, _pretty_str(name)) for name in options
        ]
