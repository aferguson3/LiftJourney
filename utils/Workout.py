from dataclasses import dataclass
from typing import Set


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
    sets: list[ExerciseSet]  # sets ordered by time

    def __init__(self):
        self.activityId = ""
        self.datetime = ""
        self.name = ""
        self.category = ""
        self.sets = ""

    def transverse_by_set(self, targetSet: int) -> list[ExerciseSet]:
        # only returns exercises with the given set number

        setNumber = 1
        matchedStepIndex = self.sets[0].stepIndex
        matchedExercise = self.sets[0].exerciseName
        matchedSets = list()
        for currSet in self.sets:
            if matchedExercise != currSet.exerciseName or matchedStepIndex != currSet.stepIndex:
                setNumber = 1
                matchedExercise = currSet.exerciseName
                matchedStepIndex = currSet.stepIndex
            if setNumber == targetSet:
                matchedSets.append(currSet)
            setNumber = setNumber + 1
        return matchedSets

    def list_exercises(self) -> set[str]:
        sets = self.transverse_by_set(1)
        exerciseNames = list()
        for currSet in sets:
            exerciseNames.append(currSet.exerciseName)

        return set(exerciseNames)
