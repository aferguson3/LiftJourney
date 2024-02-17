from dataclasses import dataclass


@dataclass(init=False)
class ExerciseSet:
    exerciseName: str
    numReps: int
    weight_grams: float
    duration_secs: float
    stepIndex: int
    startTime: str

    def __init__(self):
        exerciseName = ""
        numReps = ""
        weight_grams = ""
        duration_secs = ""
        stepIndex = ""
        startTime = ""


@dataclass
class Workout:
    activityId: str
    datetime: str
    name: str
    category: str
    sets: list[ExerciseSet]

    def __init__(self):
        activityId = ""
        datetime = ""
        name = ""
        category = ""
        sets = ""
