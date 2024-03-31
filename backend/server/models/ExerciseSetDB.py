from backend.server import db


class ExerciseSetDB(db.Model):
    __tablename__ = 'exercise_sets'
    id = db.Column(db.Integer, primary_key=True)
    duration_secs = db.Column(db.Float)
    exerciseName = db.Column(db.String(100))
    numReps = db.Column(db.Integer)
    startTime = db.Column(db.String(50))
    stepIndex = db.Column(db.Integer)
    targetReps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)

    def __init__(self, _set: dict):
        self.duration_secs = _set['duration_secs']
        self.exerciseName = _set['exerciseName']
        self.numReps = _set['numReps']
        self.startTime = _set['startTime']
        self.stepIndex = _set['stepIndex']
        self.targetReps = _set['targetReps']
        self.weight = _set['weight']

    def __repr__(self):
        return (f"exercise:{self.exerciseName} dur:{self.duration_secs}, reps:{self.numReps} start:{self.startTime} "
                f"targetReps: {self.targetReps} weight: {self.weight}")

    def get_dict(self):
        _dict = {
            "duration_secs": self.duration_secs,
            "exerciseName": self.exerciseName,
            "numReps": self.numReps,
            "startTime": self.startTime,
            "stepIndex": self.stepIndex,
            "targetReps": self.targetReps,
            "weight": self.weight
        }
        return _dict
