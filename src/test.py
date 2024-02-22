# from src.main import workouts_to_dict
import dataclasses

from src.models.Workout import Workout
from src.models.ExerciseSet import ExerciseSet
from src.manage_workouts import workouts_to_dict, load_workouts
from src.manage_workouts import sort_workouts
import xarray as xr

TEST_DATAFILE = 'data/workout_data_test.json'

wo1 = Workout()
wo1.activityId = 13989374356
wo1.datetime = "2024-02-16T13:26:04.0"
sets1 = [
    ExerciseSet(exerciseName="BARBELL_BACK_SQUAT", numReps=5, weight_grams=61250.0, duration_secs=114.723, stepIndex=2,
                startTime="2024-02-16T13:35:25.0"),
    ExerciseSet(exerciseName="BARBELL_BULGARIAN_SPLIT_SQUAT", numReps=6, weight_grams=93000.0, duration_secs=316.434,
                stepIndex=4, startTime="2024-02-16T13:38:49.0"),
    ExerciseSet(exerciseName="BARBELL_BULGARIAN_SPLIT_SQUAT", numReps=4, weight_grams=93000.0, duration_secs=266.559,
                stepIndex=4, startTime="2024-02-16T13:45:36.0"),
    ExerciseSet(exerciseName="BARBELL_BULGARIAN_SPLIT_SQUAT", numReps=4, weight_grams=93000.0, duration_secs=302.391,
                stepIndex=4, startTime="2024-02-16T13:51:32.0"),
    ExerciseSet(exerciseName="BARBELL_BULGARIAN_SPLIT_SQUAT", numReps=7, weight_grams=61250.0, duration_secs=172.538,
                stepIndex=4, startTime="2024-02-16T13:58:05.0"),
    ExerciseSet(exerciseName="ROMANIAN_DEADLIFT", numReps=6, weight_grams=106562.0, duration_secs=202.246, stepIndex=7,
                startTime="2024-02-16T14:02:27.0"),
    ExerciseSet(exerciseName="ROMANIAN_DEADLIFT", numReps=5, weight_grams=106562.0, duration_secs=219.243, stepIndex=7,
                startTime="2024-02-16T14:07:20.0"),
    ExerciseSet(exerciseName="ROMANIAN_DEADLIFT", numReps=3, weight_grams=106562.0, duration_secs=195.178, stepIndex=7,
                startTime="2024-02-16T14:12:29.0"),
    ExerciseSet(exerciseName="JUMP_SQUAT", numReps=6, weight_grams=0.0, duration_secs=82.273, stepIndex=10,
                startTime="2024-02-16T14:17:14.0"),
    ExerciseSet(exerciseName="JUMP_SQUAT", numReps=7, weight_grams=0.0, duration_secs=121.841, stepIndex=10,
                startTime="2024-02-16T14:20:06.0"),
    ExerciseSet(exerciseName="JUMP_SQUAT", numReps=6, weight_grams=0.0, duration_secs=103.599, stepIndex=10,
                startTime="2024-02-16T14:23:38.0"),
    ExerciseSet(exerciseName="STANDING_BARBELL_CALF_RAISE", numReps=20, weight_grams=111125.0, duration_secs=145.46,
                stepIndex=13, startTime="2024-02-16T14:26:52.0"),
    ExerciseSet(exerciseName="STANDING_BARBELL_CALF_RAISE", numReps=10, weight_grams=115687.0, duration_secs=74.478,
                stepIndex=13, startTime="2024-02-16T14:30:47.0"),
    ExerciseSet(exerciseName="STANDING_BARBELL_CALF_RAISE", numReps=8, weight_grams=115687.0, duration_secs=108.97,
                stepIndex=13, startTime="2024-02-16T14:33:32.0"),
    ExerciseSet(exerciseName="JUMP_SQUAT", numReps=6, weight_grams=0.0, duration_secs=83.017, stepIndex=16,
                startTime="2024-02-16T14:36:51.0"),
    ExerciseSet(exerciseName="JUMP_SQUAT", numReps=6, weight_grams=0.0, duration_secs=25.969, stepIndex=16,
                startTime="2024-02-16T14:39:14.0"),
    ExerciseSet(exerciseName="JUMP_SQUAT", numReps=10, weight_grams=0.0, duration_secs=55.533, stepIndex=16,
                startTime="2024-02-16T14:40:40.0")]
wo1.sets = sets1

wo2 = Workout()
wo2.activityId = 13975059216
wo2.datetime = "2024-02-15T13:31:41.0"
sets2 = [
    ExerciseSet(exerciseName="BARBELL_DEADLIFT", numReps=9, weight_grams=61234.0, duration_secs=310.434, stepIndex=2,
                startTime="2024-02-15T13:43:23.0"),
    ExerciseSet(exerciseName="BARBELL_DEADLIFT", numReps=4, weight_grams=93000.0, duration_secs=422.378, stepIndex=4,
                startTime="2024-02-15T13:50:03.0"),
    ExerciseSet(exerciseName="BARBELL_DEADLIFT", numReps=10, weight_grams=93000.0, duration_secs=474.054, stepIndex=4,
                startTime="2024-02-15T13:59:36.0"),
    ExerciseSet(exerciseName="BARBELL_DEADLIFT", numReps=1, weight_grams=124750.0, duration_secs=371.585, stepIndex=4,
                startTime="2024-02-15T14:10:00.0"),
    ExerciseSet(exerciseName=None, numReps=6, weight_grams=None, duration_secs=115.384, stepIndex=7,
                startTime="2024-02-15T14:18:41.0"),
    ExerciseSet(exerciseName=None, numReps=5, weight_grams=None, duration_secs=134.868, stepIndex=7,
                startTime="2024-02-15T14:22:07.0"),
    ExerciseSet(exerciseName=None, numReps=4, weight_grams=None, duration_secs=220.124, stepIndex=7,
                startTime="2024-02-15T14:25:52.0"),
    ExerciseSet(exerciseName="BARBELL_SHRUG", numReps=10, weight_grams=124750.0, duration_secs=335.055, stepIndex=10,
                startTime="2024-02-15T14:31:02.0"),
    ExerciseSet(exerciseName="BARBELL_SHRUG", numReps=2, weight_grams=124750.0, duration_secs=112.418, stepIndex=10,
                startTime="2024-02-15T14:38:07.0"),
    ExerciseSet(exerciseName="BARBELL_SHRUG", numReps=3, weight_grams=124750.0, duration_secs=137.247, stepIndex=10,
                startTime="2024-02-15T14:41:29.0"),
    ExerciseSet(exerciseName="DUMBBELL_FLYE", numReps=7, weight_grams=15875.0, duration_secs=304.408, stepIndex=13,
                startTime="2024-02-15T14:45:16.0"),
    ExerciseSet(exerciseName="DUMBBELL_FLYE", numReps=4, weight_grams=15875.0, duration_secs=188.738, stepIndex=13,
                startTime="2024-02-15T14:51:21.0"),
    ExerciseSet(exerciseName="DUMBBELL_FLYE", numReps=4, weight_grams=15875.0, duration_secs=142.55, stepIndex=13,
                startTime="2024-02-15T14:54:40.0"),
    ExerciseSet(exerciseName="DUMBBELL_BICEPS_CURL", numReps=5, weight_grams=18125.0, duration_secs=233.782,
                stepIndex=16, startTime="2024-02-15T14:58:03.0"),
    ExerciseSet(exerciseName="DUMBBELL_BICEPS_CURL", numReps=7, weight_grams=18125.0, duration_secs=168.787,
                stepIndex=16, startTime="2024-02-15T15:03:26.0"),
    ExerciseSet(exerciseName="DUMBBELL_BICEPS_CURL", numReps=3, weight_grams=18125.0, duration_secs=80.746,
                stepIndex=16, startTime="2024-02-15T15:07:45.0"),
    ExerciseSet(exerciseName="BENT_OVER_ROW_WITH_BARBELL", numReps=2, weight_grams=83937.0, duration_secs=138.44,
                stepIndex=None, startTime="2024-02-15T15:11:23.0"),
    ExerciseSet(exerciseName="BENT_OVER_ROW_WITH_BARBELL", numReps=6, weight_grams=61250.0, duration_secs=128.323,
                stepIndex=None, startTime="2024-02-15T15:17:18.0"),
    ExerciseSet(exerciseName="BENT_OVER_ROW_WITH_BARBELL", numReps=6, weight_grams=61250.0, duration_secs=61.06,
                stepIndex=None, startTime="2024-02-15T15:22:10.0")]
wo2.sets = sets2

wo3 = Workout()
wo3.activityId = 13944539762
wo3.datetime = "2024-02-13T13:19:35.0"
sets3 = [ExerciseSet(exerciseName="BARBELL_BENCH_PRESS", numReps=17, weight_grams=61250.0, duration_secs=150.134,
                     stepIndex=2, startTime="2024-02-13T13:29:25.0"),
         ExerciseSet(exerciseName="BARBELL_BENCH_PRESS", numReps=6, weight_grams=106562.0, duration_secs=173.61,
                     stepIndex=4, startTime="2024-02-13T13:33:25.0"),
         ExerciseSet(exerciseName="BARBELL_BENCH_PRESS", numReps=5, weight_grams=106562.0, duration_secs=206.07,
                     stepIndex=4, startTime="2024-02-13T13:38:19.0"),
         ExerciseSet(exerciseName="BARBELL_BENCH_PRESS", numReps=1, weight_grams=106562.0, duration_secs=171.714,
                     stepIndex=4, startTime="2024-02-13T13:43:45.0"),
         ExerciseSet(exerciseName="SMITH_MACHINE_OVERHEAD_PRESS", numReps=6, weight_grams=65750.0,
                     duration_secs=131.817, stepIndex=7, startTime="2024-02-13T13:48:37.0"),
         ExerciseSet(exerciseName="SMITH_MACHINE_OVERHEAD_PRESS", numReps=4, weight_grams=65750.0,
                     duration_secs=158.956, stepIndex=10, startTime="2024-02-13T13:53:22.0"),
         ExerciseSet(exerciseName="SMITH_MACHINE_OVERHEAD_PRESS", numReps=3, weight_grams=65750.0, duration_secs=266.54,
                     stepIndex=10, startTime="2024-02-13T13:57:31.0"),
         ExerciseSet(exerciseName="TRICEPS_PRESS", numReps=6, weight_grams=97500.0, duration_secs=162.356, stepIndex=13,
                     startTime="2024-02-13T14:03:28.0"),
         ExerciseSet(exerciseName="TRICEPS_PRESS", numReps=2, weight_grams=97500.0, duration_secs=169.884, stepIndex=13,
                     startTime="2024-02-13T14:07:40.0"),
         ExerciseSet(exerciseName="TRICEPS_PRESS", numReps=2, weight_grams=97500.0, duration_secs=154.206, stepIndex=13,
                     startTime="2024-02-13T14:12:00.0"),
         ExerciseSet(exerciseName=None, numReps=7, weight_grams=13625.0, duration_secs=125.879, stepIndex=16,
                     startTime="2024-02-13T14:16:04.0"),
         ExerciseSet(exerciseName=None, numReps=3, weight_grams=13625.0, duration_secs=100.188, stepIndex=16,
                     startTime="2024-02-13T14:19:40.0"),
         ExerciseSet(exerciseName=None, numReps=2, weight_grams=13625.0, duration_secs=150.757, stepIndex=16,
                     startTime="2024-02-13T14:22:31.0"),
         ExerciseSet(exerciseName="INCLINE_BARBELL_BENCH_PRESS", numReps=5, weight_grams=83937.0, duration_secs=179.519,
                     stepIndex=19, startTime="2024-02-13T14:26:32.0"),
         ExerciseSet(exerciseName="INCLINE_BARBELL_BENCH_PRESS", numReps=2, weight_grams=83937.0, duration_secs=117.835,
                     stepIndex=19, startTime="2024-02-13T14:31:02.0"),
         ExerciseSet(exerciseName="INCLINE_BARBELL_BENCH_PRESS", numReps=2, weight_grams=83937.0, duration_secs=89.492,
                     stepIndex=19, startTime="2024-02-13T14:34:30.0"),
         ExerciseSet(exerciseName="DUMBBELL_FLYE", numReps=7, weight_grams=15875.0, duration_secs=139.464, stepIndex=7,
                     startTime="2024-02-13T14:37:50.0"),
         ExerciseSet(exerciseName="DUMBBELL_FLYE", numReps=12, weight_grams=2250.0, duration_secs=198.998, stepIndex=7,
                     startTime="2024-02-13T14:41:39.0"),
         ExerciseSet(exerciseName="DUMBBELL_LYING_TRICEPS_EXTENSION", numReps=7, weight_grams=18125.0,
                     duration_secs=168.83, stepIndex=22, startTime="2024-02-13T14:46:28.0"),
         ExerciseSet(exerciseName="DUMBBELL_LYING_TRICEPS_EXTENSION", numReps=5, weight_grams=18125.0,
                     duration_secs=153.592, stepIndex=22, startTime="2024-02-13T14:50:47.0"),
         ExerciseSet(exerciseName="DUMBBELL_LYING_TRICEPS_EXTENSION", numReps=3, weight_grams=18125.0,
                     duration_secs=221.957, stepIndex=22, startTime="2024-02-13T14:54:51.0")]
wo3.sets = sets3

workouts = [wo1, wo2, wo3]
data_dict = workouts_to_dict(workouts)
# --------SORTING WORKOUTS OR SETS-----------------
# lists = sort_workouts(workouts[0], 'category')
# lists = sort_workouts(workouts[0], 'exerciseName')
# lists = sort_workouts(workouts, 'exerciseName')
# lists = sort_workouts(workouts, 'datetime')

pass
# ---------BACKUP/LOAD WORKOUTS-------------------
# dump_to_json(data_dict, TEST_DATAFILE, 'w')
# loaded_data = load_workouts(TEST_DATAFILE)
# print(f"Data loaded correctly: {loaded_data == workouts}")


# new_list = sorted(workouts, key=)


# time_dims = [v["datetime"] for (k, v) in loaded_data.items()]
# sets_dims = [range(1, len(v["sets"]) + 1) for (k, v) in loaded_data.items()]
#
# ds = xr.Dataset(data_vars={
#     "duration": (("datetime", "sets"),),
#     "name": "",
#     "reps": "",
#     "weight": "",
#     "stepIndex": ""
# }, coords={
#     "datetime": time_dims,
#     "sets": sets_dims
# })
