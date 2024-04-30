from flask_wtf import FlaskForm
from wtforms import SelectField


def _pretty_str(name: str):
    return name.replace("_", " ")


class CategoryField(FlaskForm):
    categories = SelectField('Categories')

    def set_choices(self, options: list[str]):
        self.categories.choices = ([("None", "-- Select a Category --")] +
                                   [(name, _pretty_str(name)) for name in options])


class ExerciseField(FlaskForm):
    exercises = SelectField('Exercises')

    def set_choices(self, options: list[str]):
        self.exercises.choices = [(name, _pretty_str(name)) for name in options]


class RepRangeField(FlaskForm):
    rep_ranges = SelectField('Rep_ranges')

    def set_choices(self, options: list[float]):
        self.rep_ranges.choices = [("None", "No Filter")] + [(option, int(option)) for option in options]
