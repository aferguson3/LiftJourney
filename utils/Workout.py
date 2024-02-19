from dataclasses import dataclass


@dataclass
class ExerciseSet:
    exerciseName: str
    numReps: int
    weight_grams: float
    duration_secs: float
    stepIndex: int
    startTime: str

    def __init__(self,
                 exerciseName=None,
                 numReps=None,
                 weight_grams=None,
                 duration_secs=None,
                 stepIndex=None,
                 startTime=None):
        self.exerciseName = exerciseName
        self.numReps = numReps
        self.weight_grams = weight_grams
        self.duration_secs = duration_secs
        self.stepIndex = stepIndex
        self.startTime = startTime

    def __dict__(self) -> dict:
        _dict = {
            "exerciseName": self.exerciseName,
            "numReps": self.numReps,
            "weight_grams": self.weight_grams,
            "duration_secs": self.duration_secs,
            "stepIndex": self.stepIndex,
            "startTime": self.startTime
        }
        return _dict


@dataclass
class Workout:
    activityId: str
    datetime: str
    name: str
    category: str
    sets: list[ExerciseSet]  # sets ordered by time

    def __init__(self,
                 activityId=None,
                 datetime=None,
                 name=None,
                 category=None,
                 sets=None):
        self.activityId = activityId
        self.datetime = datetime
        self.name = name
        self.category = category
        self.sets = sets

    def __sets_to_dict__(self) -> list:
        _list = list()
        length = len(self.sets)
        for index, currSet in zip(range(1, length), self.sets):
            _list.append(currSet.__dict__())

        keys = list(range(1, len(self.sets)))
        sets_dict = {key: value for (key, value) in zip(keys, _list)}
        return sets_dict

    def __dict__(self) -> dict:
        _dict = {
            "activityId": self.activityId,
            "datetime": self.datetime,
            "name": self.name,
            "category": self.category,
            "sets": self.__sets_to_dict__()
        }
        return _dict

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
