import dataclasses
from dataclasses import dataclass


@dataclass
class ExerciseSet:
    duration_secs: float
    exerciseName: str
    numReps: int
    targetReps: int
    startTime: str
    stepIndex: int
    weight: float

    def __init__(self,
                 duration_secs=None,
                 exerciseName=None,
                 numReps=None,
                 startTime=None,
                 stepIndex=None,
                 weight=None,
                 targetReps=None,
                 loading_dict: dict | None = None):
        if isinstance(loading_dict, dict):
            self.duration_secs = loading_dict["duration_secs"] if "duration_secs" in loading_dict else None
            self.exerciseName = loading_dict["exerciseName"] if "exerciseName" in loading_dict else None
            self.numReps = loading_dict["numReps"] if "numReps" in loading_dict else None
            self.targetReps = loading_dict["targetReps"] if "targetReps" in loading_dict else None
            self.startTime = loading_dict["startTime"] if "startTime" in loading_dict else None
            self.stepIndex = loading_dict["stepIndex"] if "stepIndex" in loading_dict else None
            self.weight = loading_dict["weight"] if "weight" in loading_dict else None
            return

        self.duration_secs = duration_secs
        self.exerciseName = exerciseName
        self.numReps = numReps
        self.targetReps = targetReps
        self.startTime = startTime
        self.stepIndex = stepIndex
        self.weight = weight

    def asdict(self):
        return dataclasses.asdict(self)
