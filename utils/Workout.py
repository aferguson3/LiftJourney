from dataclasses import dataclass


@dataclass
class ExerciseSet:
    exerciseName: str
    numReps: int
    weight_grams: float
    duration_secs: float
    stepIndex: int
    startTime: str

    def __init__(self):
        self.exerciseName = ""
        self.numReps = ""
        self.weight_grams = ""
        self.duration_secs = ""
        self.stepIndex = ""
        self.startTime = ""


@dataclass
class Workout:
    activityId: str
    datetime: str
    name: str
    category: str
    sets: list[ExerciseSet]

    def __init__(self):
        self.activityId = ""
        self.datetime = ""
        self.name = ""
        self.category = ""
        self.sets = ""
