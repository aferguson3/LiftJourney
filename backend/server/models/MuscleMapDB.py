from backend.server.config import db

MUSCLE_GROUPS_LIST = sorted(["Arms", "Chest", "Core", "Back", "Legs", "Shoulders"])


class MuscleMapDB(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True)
    exerciseName = db.Column(db.String(100))
    category = db.Column(db.String(50))

    def __init__(self, exerciseName, category):
        self.exerciseName: str = exerciseName
        self.category: str | None = category

    def __repr__(self):
        class_name = type(self).__name__
        return (
            f"{class_name}(exerciseName={self.exerciseName}, category={self.category})"
        )

    def get_dict(self):
        return {"exerciseName": self.exerciseName, "category": self.category}


def dict_to_muscleMapDB(values: dict) -> list[MuscleMapDB]:
    exercises = list()
    for key, value in values.items():
        exercises.append(MuscleMapDB(exerciseName=key, category=value))
    return exercises
