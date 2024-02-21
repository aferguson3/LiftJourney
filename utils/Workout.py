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


@dataclass
class Workout:
    activityId: str
    category: str
    datetime: str
    name: str
    sets: list[ExerciseSet]  # most recent --> oldest
    isIncomplete: bool = False

    def __init__(self,
                 activityId=None,
                 category=None,
                 datetime=None,
                 name=None,
                 sets=None):
        self.activityId = activityId
        self.category = category
        self.datetime = datetime
        self.name = name
        self.sets = sets

    def asdict(self) -> dict:
        return dataclasses.asdict(self)

    def view_sets(self) -> list[dict]:
        _list = [s.asdict() for s in self.sets]
        return _list

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

    def load(self, data: dict):
        self.activityId = self.key_search(data, "activityId")
        self.category = self.key_search(data, "category")
        self.datetime = self.key_search(data, "datetime")
        self.name = self.key_search(data, "name")

        _sets = self.key_search(data, "sets")
        self.sets = [ExerciseSet(loading_dict=s) for s in _sets]

    def key_search(self, data: dict, key_match: str) -> str | None:
        for (key, value) in data.items():
            if key == key_match:
                return value
            if isinstance(value, dict):
                return self.key_search(value, key_match)
            elif isinstance(value, list):
                for item in value:
                    return self.key_search(item, key_match)
        return None

    def validation_check(self):
        # checks if set data is incomplete
        for currSet in self.sets:
            self.isIncomplete = False
            if currSet.exerciseName is None:
                self.isIncomplete = True  # TODO: cross-reference scheduled workouts and fix errors
                return
