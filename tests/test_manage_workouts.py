import json
import os

import pytest

from src.manage_workouts import workouts_to_dict, dump_to_json, load_workouts
from src.models import Workout, ExerciseSet
from tests.sample_data import wo1, wo2, wo3


class TestManageWorkouts:

    @pytest.fixture(autouse=True)
    def init_tests(self):
        self.workout1: Workout = wo1
        self.workout2: Workout = wo2
        self.workout3: Workout = wo3
        self.allworkouts: list[Workout] = [wo1, wo2, wo3]

    def test_workouts_to_dict(self):
        assert workouts_to_dict(self.allworkouts)["workouts"] is not None
        assert workouts_to_dict([self.workout1])["workouts"] is not None
        assert workouts_to_dict([self.workout1, self.workout2])["workouts"] is not None

    def test_dump_to_json_valid(self, tmp_path):
        _sets = [ExerciseSet(exerciseName="PULL UPS", numReps=10, duration_secs=150),
                 ExerciseSet(exerciseName="BENCH", numReps=5, duration_secs=10, weight_grams=1000)]
        self.workout1.sets = _sets
        # Create a temporary directory for the test
        temp_file = os.path.join(tmp_path, "test.json")

        # Call the function with valid data and options
        dump_to_json(workouts_to_dict([self.workout1]), temp_file, "w")

        # Read the JSON file and validate the data
        with open(temp_file, "r") as file:
            loaded_data = json.load(file)
            assert loaded_data == workouts_to_dict([self.workout1])

    # Test function for FileNotFoundError
    def test_dump_to_json_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            # Call the function with a non-existent filepath
            dump_to_json(self.workout1.asdict(), "/path/to/nonexistent/file.json", "w")

    # Test function for TypeError
    def test_dump_to_json_type_error(self, tmp_path):
        temp_file = os.path.join(tmp_path, "test.json")

        with pytest.raises(TypeError):
            # Call the function with invalid data type
            dump_to_json("invalid_data", temp_file, "w")

    # Test function for invalid options
    def test_dump_to_json_invalid_option(self, tmp_path):
        with pytest.raises(ValueError):
            # Call the function with an invalid option
            dump_to_json(self.workout1.asdict(), os.path.join(tmp_path, "test.json"), "x")

    @pytest.fixture
    def sample_json_data(self, tmp_path):
        data = {
            "workouts": [
                {"activityId": "123", "category": "Strength", "datetime": "2024-02-22T10:00:00", "name": "Workout 1",
                 "sets": []},
                {"activityId": "456", "category": "Cardio", "datetime": "2024-02-23T10:00:00", "name": "Workout 2",
                 "sets": []}
            ]
        }
        file_path = os.path.join(tmp_path, "test.json")
        with open(file_path, "w") as file:
            json.dump(data, file)
        return file_path

    # Test function for loading workouts from a JSON file
    def test_load_workouts(self, sample_json_data):
        # Call the function with the sample JSON file
        result = load_workouts(sample_json_data)

        # Verify that the result is a list of Workout objects
        assert isinstance(result, list)
        assert all(isinstance(workout, Workout) for workout in result)

        # Verify the number of loaded workouts
        assert len(result) == 2

        # Verify the attributes of the first loaded workout
        assert result[0].activityId == "123"
        assert result[0].category == "Strength"
        assert result[0].datetime == "2024-02-22T10:00:00"
        assert result[0].name == "Workout 1"

        # Verify the attributes of the second loaded workout
        assert result[1].activityId == "456"
        assert result[1].category == "Cardio"
        assert result[1].datetime == "2024-02-23T10:00:00"
        assert result[1].name == "Workout 2"

    # Test function for handling FileNotFoundError
    def test_load_workouts_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            # Call the function with a non-existent file path
            load_workouts("/path/to/nonexistent/file.json")
