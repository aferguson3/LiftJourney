from flask_wtf import FlaskForm
from wtforms import SelectField


class CategoriesForm(FlaskForm):
    categories = SelectField('Categories')

    def set_choices(self, options: list[str]):
        self.categories.choices = ""


class ExercisesForm(FlaskForm):
    exercises = SelectField('Exercises')

    @staticmethod
    def _pretty_str(name: str):
        return name.replace("_", " ")

    def set_choices(self, options: list[str]):
        self.exercises.choices = [(name, self._pretty_str(name)) for name in options]


class RepRangesForm(FlaskForm):
    rep_ranges = SelectField('Rep_ranges')

    def set_choices(self, options: list[float]):
        self.rep_ranges.choices = [("None", "None")] + [(option, int(option)) for option in options]
