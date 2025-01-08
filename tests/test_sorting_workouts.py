import pytest

from backend.server.models import Workout, ExerciseSet
from backend.src.WorkoutManagement import WorkoutManagement as WorkoutManage


class TestSortingWorkouts:

    @pytest.fixture
    def sample_workouts(self):
        workouts = [
            Workout(
                activityId="1",
                category="Strength",
                datetime="2024-02-22T10:00:00",
                name="Workout 1",
                sets=[ExerciseSet(exerciseName="Squat", numReps=10)],
            ),
            Workout(
                activityId="2",
                category="Cardio",
                datetime="2024-02-23T10:00:00",
                name="Workout 2",
                sets=[ExerciseSet(exerciseName="Run", duration_secs=300)],
            ),
            Workout(
                activityId="3",
                category="Strength",
                datetime="2024-02-24T10:00:00",
                name="Workout 3",
                sets=[ExerciseSet(exerciseName="Push-up", numReps=15)],
            ),
            Workout(
                activityId="4",
                category="Strength",
                datetime="2024-02-24T10:00:00",
                name="Workout 3",
                sets=[
                    ExerciseSet(exerciseName="Push-up", numReps=None),
                    ExerciseSet(exerciseName="Push-up", numReps=None),
                ],
            ),
            Workout(
                activityId="5",
                category="Strength",
                datetime="2024-02-24T10:00:00",
                name="Workout 3",
                sets=[
                    ExerciseSet(exerciseName="Push-up", numReps=20),
                    ExerciseSet(exerciseName="Push-up", numReps=2),
                ],
            ),
        ]
        return workouts

    # Test function for sorting Workout objects by a specified key
    def test_sort_workouts_workout_key(self, sample_workouts):
        # Call the function to sort Workout objects by the 'datetime' key
        sorted_workouts = WorkoutManage.sort_workouts(sample_workouts, key="datetime")
        sorted_workouts2 = WorkoutManage.sort_workouts(sample_workouts, key="category")

        # Verify that the result is a list
        assert isinstance(sorted_workouts, list)

        # Verify that the Workout objects are sorted correctly
        assert sorted_workouts[0].datetime == "2024-02-22T10:00:00"
        assert sorted_workouts[1].datetime == "2024-02-23T10:00:00"
        assert sorted_workouts[2].datetime == "2024-02-24T10:00:00"
        assert sorted_workouts[3].datetime == "2024-02-24T10:00:00"
        assert sorted_workouts[4].datetime == "2024-02-24T10:00:00"

        assert sorted_workouts2[0].category == "Cardio"
        assert sorted_workouts2[1].category == "Strength"
        assert sorted_workouts2[2].category == "Strength"
        assert sorted_workouts2[3].category == "Strength"
        assert sorted_workouts2[4].category == "Strength"

    def test_sort_workouts_exercise_set_key(self, sample_workouts):
        assert WorkoutManage.sort_workouts(sample_workouts, "exerciseName") is None
        assert WorkoutManage.sort_workouts(sample_workouts, "numRep") is None

    # Test function for sorting ExerciseSet objects by a specified key
    def test_sort_sets_exercise_set_key(self, sample_workouts):
        # Call the function to sort ExerciseSet objects by the 'numReps' key
        sorted_exercise_sets: list[ExerciseSet] = WorkoutManage.sort_workouts(
            sample_workouts[0], key="numReps"
        )
        sorted_exercise_sets2: list[ExerciseSet] = WorkoutManage.sort_workouts(
            sample_workouts[4], key="numReps"
        )
        sorted_exercise_sets2_r: list[ExerciseSet] = WorkoutManage.sort_workouts(
            sample_workouts[4], key="numReps", reverse=True
        )

        # Verify that the result is a list
        assert isinstance(sorted_exercise_sets, list)
        # Verify that the ExerciseSet objects are sorted correctly
        assert sorted_exercise_sets[0].numReps == 10
        assert (sorted_exercise_sets2[0].numReps, sorted_exercise_sets2[1].numReps) == (
            2,
            20,
        )
        assert (
            sorted_exercise_sets2_r[0].numReps,
            sorted_exercise_sets2_r[1].numReps,
        ) == (20, 2)

    def test_sort_set_workout_key(self, sample_workouts):
        assert WorkoutManage.sort_workouts(sample_workouts[1], "datetime") is None
        assert WorkoutManage.sort_workouts(sample_workouts[2], "category") is None

    # Test function for handling invalid sorting key
    def test_sort_workouts_invalid_key(self, sample_workouts):
        # Call the function with an invalid key
        result = WorkoutManage.sort_workouts(sample_workouts[0], key="invalid_key")
        result1 = WorkoutManage.sort_workouts(sample_workouts, key="invalid_key")

        # Verify that the result is None
        assert result is None
        assert result1 is None

    @pytest.fixture
    def sample_workouts_with_none_key(self):
        workouts = [
            Workout(
                activityId="1",
                category="Strength",
                datetime="2024-02-22T10:00:00",
                name="Workout 1",
                sets=[ExerciseSet(exerciseName="Squat", numReps=2)],
            ),
            Workout(
                activityId="2",
                category=None,
                datetime="2024-02-23T10:00:00",
                name="Workout 2",
                sets=[
                    ExerciseSet(exerciseName="Squat", numReps=20),
                    ExerciseSet(exerciseName="Run", duration_secs=300, numReps=None),
                    ExerciseSet(exerciseName="Squat", numReps=1),
                ],
            ),
            Workout(
                activityId="3",
                category="Strength",
                datetime="2024-02-24T10:00:00",
                name="Workout 3",
                sets=[
                    ExerciseSet(exerciseName="Push-up", numReps=None),
                    ExerciseSet(exerciseName="Push-up", numReps=None),
                ],
            ),
        ]
        return workouts

    # Test functions for handling TypeError when comparing sets with None values in the key
    def test_sort_single_set_exercise_set_key(self, sample_workouts_with_none_key):
        assert (
            WorkoutManage.sort_workouts(sample_workouts_with_none_key[0], "numReps")
            == sample_workouts_with_none_key[0].sets
        )

    def test_sort_sets_with_one_None_set(self, sample_workouts_with_none_key):
        with pytest.raises(TypeError):
            result = WorkoutManage.sort_workouts(
                sample_workouts_with_none_key[1], key="numReps"
            )
            assert result is None

    def test_sort_sets_with_all_None_sets(self, sample_workouts_with_none_key):
        with pytest.raises(TypeError):
            result = WorkoutManage.sort_workouts(
                sample_workouts_with_none_key[2], key="numReps"
            )
            assert result is None

    def test_sort_workouts_with_one_None_workout(self, sample_workouts_with_none_key):
        with pytest.raises(TypeError):
            result = WorkoutManage.sort_workouts(
                sample_workouts_with_none_key, key="category"
            )
            assert result is None
