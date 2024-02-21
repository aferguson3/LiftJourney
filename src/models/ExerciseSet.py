import dataclasses
from dataclasses import dataclass


@dataclass
class ExerciseSet:
    duration_secs: float
    exerciseName: str
    numReps: int
    startTime: str
    stepIndex: int
    weight_grams: float

    def __init__(self,
                 duration_secs=None,
                 exerciseName=None,
                 numReps=None,
                 startTime=None,
                 stepIndex=None,
                 weight_grams=None,
                 loading_dict: dict = None):
        if isinstance(loading_dict, dict):
            self.duration_secs = loading_dict["duration_secs"] if "duration_secs" in loading_dict else None
            self.exerciseName = loading_dict["exerciseName"] if "exerciseName" in loading_dict else None
            self.numReps = loading_dict["numReps"] if "numReps" in loading_dict else None
            self.startTime = loading_dict["startTime"] if "startTime" in loading_dict else None
            self.stepIndex = loading_dict["stepIndex"] if "stepIndex" in loading_dict else None
            self.weight_grams = loading_dict["weight_grams"] if "weight_grams" in loading_dict else None
            return

        self.duration_secs = duration_secs
        self.exerciseName = exerciseName
        self.numReps = numReps
        self.startTime = startTime
        self.stepIndex = stepIndex
        self.weight_grams = weight_grams

    def asdict(self):
        return dataclasses.asdict(self)
