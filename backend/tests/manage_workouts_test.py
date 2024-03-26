import json
import os

import pytest

from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout, ExerciseSet
from backend.tests.sample_data import sets1, sets2, sets3


class TestManageWorkouts:

    @pytest.fixture
    def init_workouts(self):
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

        return wo1, wo2, wo3, [wo1, wo2, wo3]

    @pytest.fixture(autouse=True)
    def init_tests(self, init_workouts):
        self.workout1, self.workout2, self.workout3, self.all_workouts = init_workouts

    def test_workouts_to_dict(self):
        assert Manager.workouts_to_dict(self.all_workouts)["workouts"] is not None
        assert Manager.workouts_to_dict([self.workout1])["workouts"] is not None
        assert Manager.workouts_to_dict([self.workout1, self.workout2])["workouts"] is not None

    def test_dump_to_json_valid(self, tmp_path):
        _sets = [ExerciseSet(exerciseName="PULL UPS", numReps=10, duration_secs=150),
                 ExerciseSet(exerciseName="BENCH", numReps=5, duration_secs=10, weight=100)]
        self.workout1.sets = _sets
        # Create a temporary directory for the test
        temp_file = os.path.join(tmp_path, "test.json")

        # Call the function with valid data and options
        Manager.dump_to_json(Manager.workouts_to_dict([self.workout1]), temp_file, "w")

        # Read the JSON file and validate the data
        with open(temp_file, "r") as file:
            loaded_data = json.load(file)
            assert loaded_data == Manager.workouts_to_dict([self.workout1])

    # Test function for FileNotFoundError
    def test_dump_to_json_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            # Call the function with a non-existent filepath
            Manager.dump_to_json(self.workout1.asdict(), "/path/to/nonexistent/file.json", "w")

    # Test function for TypeError
    def test_dump_to_json_type_error(self, tmp_path):
        temp_file = os.path.join(tmp_path, "test.json")

        with pytest.raises(TypeError):
            # Call the function with invalid data type
            Manager.dump_to_json("invalid_data", temp_file, "w")

    # Test function for invalid options
    def test_dump_to_json_invalid_option(self, tmp_path):
        with pytest.raises(ValueError):
            # Call the function with an invalid option
            Manager.dump_to_json(self.workout1.asdict(), os.path.join(tmp_path, "test.json"), "x")

    @pytest.fixture
    def test_metadata(self):
        metadata = {"numWorkouts": "", "filepath": "",
                    "dates": {"firstWorkout": "", "lastWorkout": ""},
                    "start": 0, "limit": 0
                    }
        return metadata

    def test_dump_to_json_correct_metadata(self, tmp_path, test_metadata):
        _metadata = test_metadata
        _metadata["filepath"] = os.path.join(tmp_path, 'metadata.json')

        sorted_workouts = Manager.sort_workouts(self.all_workouts, 'datetime')
        Manager.dump_to_json(Manager.workouts_to_dict(sorted_workouts), os.path.join(tmp_path, "test.json"), 'w',
                             _metadata)

        with open(os.path.join(tmp_path, "metadata.json")) as file:
            metadata = json.load(file)

        assert metadata is not None
        assert metadata["numWorkouts"] == 3
        assert metadata["dates"]["firstWorkout"] == "2024-02-13T13:19:35.0"
        assert metadata["dates"]["lastWorkout"] == "2024-02-16T13:26:04.0"

    def test_dump_to_json_metadata_file_not_found(self, tmp_path, test_metadata):
        # Test for FileNotFoundError for metadata
        metadata = test_metadata
        with pytest.raises(FileNotFoundError):
            Manager.dump_to_json(Manager.workouts_to_dict([self.workout1]), os.path.join(tmp_path, "test.json"), "w",
                                 metadata)

    @pytest.fixture
    def sample_json_data_file(self, tmp_path):
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
    def test_load_workouts(self, sample_json_data_file):
        # Call the function with the sample JSON file
        result = Manager.load_workouts(sample_json_data_file)

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
            Manager.load_workouts("/path/to/nonexistent/file.json")

    def test_view_sets_from_workout(self):
        setsData = Manager.view_sets_from_workouts(self.all_workouts)

        assert setsData is not None
        assert len(setsData["duration_secs"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(
            self.workout3.sets)
        assert len(setsData["exerciseName"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(
            self.workout3.sets)
        assert len(setsData["numReps"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(self.workout3.sets)
        assert len(setsData["targetReps"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(
            self.workout3.sets)
        assert len(setsData["startTime"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(self.workout3.sets)
        assert len(setsData["stepIndex"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(self.workout3.sets)
        assert len(setsData["weight"]) == len(self.workout1.sets) + len(self.workout2.sets) + len(self.workout3.sets)
