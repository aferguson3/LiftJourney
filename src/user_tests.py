from src.manage_workouts import workouts_to_dict
from src.models.Workout import Workout
from tests.sample_data import sets1, sets2, sets3

TEST_DATAFILE = './data/workout_data_test.json'

wo1 = Workout()
wo1.activityId = 13989374356
wo1.datetime = "2024-02-16T13:26:04.0"
wo1.sets = sets1

wo2 = Workout()
wo2.activityId = 13975059216
wo2.datetime = "2024-02-15T13:31:41.0"
wo2.sets = sets2

wo3 = Workout()
wo3.activityId = 13944539762
wo3.datetime = "2024-02-13T13:19:35.0"
wo3.sets = sets3

workouts = [wo1, wo2, wo3]
list_workouts = workouts_to_dict(workouts)["workouts"]

pass
