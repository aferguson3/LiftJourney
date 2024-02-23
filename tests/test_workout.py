from src.models import ExerciseSet, Workout
from tests.sample_data import sets1, sets2, sets3
import pytest


class TestWorkout:

    @pytest.fixture
    def load_workouts(self):
        wo1 = Workout()
        wo1.activityId = 77789374356
        wo1.datetime = "2024-02-16T13:26:04.0"
        wo1.sets = sets1

        wo2 = Workout()
        wo2.activityId = 22944539762
        wo2.datetime = "2024-02-13T13:19:35.0"
        wo2.sets = sets2

        wo3 = Workout()
        wo3.activityId = 10297505921
        wo3.datetime = "2024-02-15T13:31:41.0"
        wo3.sets = sets3

        return wo1, wo2, wo3

    @pytest.fixture(autouse=True)
    def init_tests(self, load_workouts):
        self.workout1, self.workout2, self.workout3 = load_workouts

    def test_workout_asdict(self):
        assert self.workout1.asdict() is not None
        assert self.workout2.asdict() is not None
        assert self.workout3.asdict() is not None

    @pytest.fixture
    def sample_workout(self):
        _dict = {'activityId': 10297505921, 'category': "UPPER", 'datetime': '2024-02-15T13:31:41.0', 'name': "John",
                 'sets': [{'duration_secs': 310.434, 'exerciseName': 'BARBELL_DEADLIFT', 'numReps': 9,
                           'startTime': '2024-02-15T13:43:23.0', 'stepIndex': 2, 'weight_grams': 61234.0},
                          {'duration_secs': 422.378, 'exerciseName': 'BARBELL_DEADLIFT', 'numReps': 4,
                           'startTime': '2024-02-15T13:50:03.0', 'stepIndex': 4, 'weight_grams': 93000.0},
                          {'duration_secs': 474.054, 'exerciseName': 'BARBELL_DEADLIFT', 'numReps': 10,
                           'startTime': '2024-02-15T13:59:36.0', 'stepIndex': 4, 'weight_grams': 93000.0},
                          ],
                 'isIncomplete': False}
        return _dict

    def test_workout_init_workout(self, sample_workout):
        new_workout = Workout()
        new_workout.init_workout(sample_workout)

        assert new_workout is not None
        assert new_workout.activityId is not None
        assert new_workout.category is not None
        assert new_workout.datetime is not None
        assert new_workout.name is not None
        assert new_workout.sets is not None
        assert new_workout.isIncomplete is not None
        assert new_workout.sets[0] != new_workout.sets[1] != new_workout.sets[2]

    def test_workout_view_sets(self, sample_workout):
        # Check if the view_sets method returns a non-empty list
        new_workout = Workout()
        new_workout.init_workout(sample_workout
                                 )
        assert new_workout.view_sets() is not None
        assert self.workout1.view_sets() is not None
        assert self.workout2.view_sets() is not None

        # Check if the number of sets returned matches the expected length
        assert len(new_workout.sets) == 3
        assert len(self.workout2.sets) == 10
        assert len(self.workout3.sets) == 10

        # Check if the expected keys & values are present
        for set_data in new_workout.view_sets():
            assert 'stepIndex' in set_data
            assert 'exerciseName' in set_data
            assert 'numReps' in set_data
            assert 'weight_grams' in set_data
            assert 'duration_secs' in set_data
            assert 'startTime' in set_data

            assert set_data['stepIndex'] is not None
            assert set_data['exerciseName'] is not None
            assert set_data['numReps'] is not None
            assert set_data['weight_grams'] is not None
            assert set_data['duration_secs'] is not None
            assert set_data['startTime'] is not None

    def test_workout_transverse_by_set_number(self):
        def get_exercise_name(data: list[ExerciseSet]):
            return [_sets.exerciseName for _sets in data]

        result_set0 = self.workout2.transverse_by_set_number(0)
        result_set1 = self.workout2.transverse_by_set_number(1)
        result_set2 = self.workout2.transverse_by_set_number(2)
        result_set3_w2 = self.workout2.transverse_by_set_number(3)

        result_set3_w3 = self.workout3.transverse_by_set_number(3)
        result_set4 = self.workout3.transverse_by_set_number(4)
        result_set5 = self.workout3.transverse_by_set_number(5)

        assert result_set0 == []
        assert (get_exercise_name(result_set1) ==
                ['BARBELL_BENCH_PRESS', 'BARBELL_BENCH_PRESS', 'SMITH_MACHINE_OVERHEAD_PRESS',
                 'SMITH_MACHINE_OVERHEAD_PRESS', None])
        assert (get_exercise_name(result_set2) ==
                ['BARBELL_BENCH_PRESS', 'SMITH_MACHINE_OVERHEAD_PRESS', None])
        assert get_exercise_name(result_set3_w2) == ['BARBELL_BENCH_PRESS', None]

        assert get_exercise_name(result_set3_w3) == ['BARBELL_DEADLIFT', None, 'BARBELL_SHRUG']
        assert result_set4 == []
        assert result_set5 == []

    def test_workout_list_exercises(self):
        # Tests the list_exercises method and transverse_by_set_number(1)
        expected1 = ["BARBELL_BACK_SQUAT", "BARBELL_BULGARIAN_SPLIT_SQUAT", "JUMP_SQUAT", "ROMANIAN_DEADLIFT"]
        expected2 = ["BARBELL_BENCH_PRESS", "SMITH_MACHINE_OVERHEAD_PRESS", None]
        expected3 = ["BARBELL_DEADLIFT", "BARBELL_SHRUG", None]

        assert self.workout1.list_exercises() == expected1
        assert self.workout2.list_exercises() == expected2
        assert self.workout3.list_exercises() == expected3

    @pytest.fixture
    def key_search_data(self):
        sets = [{'duration_secs': 310.434, 'exerciseName': 'BARBELL_DEADLIFT', 'numReps': 9,
                 'startTime': '2024-02-15T13:43:23.0', 'stepIndex': 2, 'weight_grams': 61234.0},
                {'duration_secs': 474.054, 'exerciseName': 'BARBELL_DEADLIFT', 'numReps': 10,
                 'startTime': '2024-02-15T13:59:36.0', 'stepIndex': 4, 'weight_grams': 93000.0},
                ]
        data = {'activityId': 123, 'category': "LEGS", 'datetime': '2024-02-22T10:00:00', 'name': "Morning",
                'sets': sets,
                'isIncomplete': False}
        return data, sets

    @pytest.fixture
    def test_workout_key_search_workout_keys(self, key_search_data):
        data, sets = key_search_data
        # Test key_search for each key in the Workout dictionary
        assert Workout.key_search(data, "activityId") == 123
        assert Workout.key_search(data, "category") == "LEGS"
        assert Workout.key_search(data, "datetime") == "2024-02-22T10:00:00"
        assert Workout.key_search(data, "name") == "Morning"
        assert Workout.key_search(data, "isIncomplete") is False
        assert Workout.key_search(data, "sets") == sets

    def test_workout_key_search_set_keys(self, key_search_data):
        data, sets = key_search_data
        # Testing ExerciseSet keys
        assert Workout.key_search(data, "duration_secs") is None
        assert Workout.key_search(data, "exerciseName") is None
        assert Workout.key_search(data, "numReps") is None
        assert Workout.key_search(data, "startTime") is None
        assert Workout.key_search(data, "stepIndex") is None
        assert Workout.key_search(data, "weight_grams") is None

    def test_workout_validation_check(self):
        sets_not_None = [ExerciseSet(exerciseName="BENCH"), ExerciseSet(exerciseName="CURLS"),
                         ExerciseSet(exerciseName="SQUAT")]
        sets_None = [ExerciseSet(exerciseName=None), ExerciseSet(exerciseName=None),
                     ExerciseSet(exerciseName=None)]
        sets_None2 = [ExerciseSet(exerciseName="BENCH"), ExerciseSet(exerciseName="CURLS"),
                      ExerciseSet(exerciseName=None)]

        self.workout3.sets = sets_not_None
        self.workout3.validation_check()
        assert self.workout3.isIncomplete is False

        self.workout3.sets = sets_None
        self.workout3.validation_check()
        assert self.workout3.isIncomplete is True

        self.workout3.sets = sets_None2
        self.workout3.validation_check()
        assert self.workout3.isIncomplete is True
