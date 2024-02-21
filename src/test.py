# from src.main import workouts_to_dict
from utils.Workout import Workout, ExerciseSet
from src.main import dump_data, workouts_to_dict, load_data

TEST_DATAFILE = '../data/workout_data_test.json'
# Raw ActivityID data
# {"activityId": 13975059216, "exerciseSets": [{"exercises": [{"category": "INDOOR_BIKE", "name": false, "probability": 100.0}], "duration": 173.84, "repetitionCount": false, "weight": 0.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:31:41.0", "wktStepIndex": 0, "messageIndex": 0}, {"exercises": [], "duration": 528.186, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T13:34:35.0", "wktStepIndex": 1, "messageIndex": 1}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 310.434, "repetitionCount": 9, "weight": 61234.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:43:23.0", "wktStepIndex": 2, "messageIndex": 2}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T13:48:33.0", "wktStepIndex": 3, "messageIndex": 3}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 422.378, "repetitionCount": 4, "weight": 93000.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:50:03.0", "wktStepIndex": 4, "messageIndex": 4}, {"exercises": [], "duration": 150.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T13:57:06.0", "wktStepIndex": 5, "messageIndex": 5}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 474.054, "repetitionCount": 10, "weight": 93000.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:59:36.0", "wktStepIndex": 4, "messageIndex": 6}, {"exercises": [], "duration": 150.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:07:30.0", "wktStepIndex": 5, "messageIndex": 7}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 371.585, "repetitionCount": 1, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:10:00.0", "wktStepIndex": 4, "messageIndex": 8}, {"exercises": [], "duration": 150.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:16:11.0", "wktStepIndex": 5, "messageIndex": 9}, {"exercises": [{"category": "PULL_UP", "name": false, "probability": 100.0}], "duration": 115.384, "repetitionCount": 6, "weight": false, "setType": "ACTIVE", "startTime": "2024-02-15T14:18:41.0", "wktStepIndex": 7, "messageIndex": 10}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:20:37.0", "wktStepIndex": 8, "messageIndex": 11}, {"exercises": [{"category": "PULL_UP", "name": false, "probability": 100.0}], "duration": 134.868, "repetitionCount": 5, "weight": false, "setType": "ACTIVE", "startTime": "2024-02-15T14:22:07.0", "wktStepIndex": 7, "messageIndex": 12}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:24:22.0", "wktStepIndex": 8, "messageIndex": 13}, {"exercises": [{"category": "PULL_UP", "name": false, "probability": 100.0}], "duration": 220.124, "repetitionCount": 4, "weight": false, "setType": "ACTIVE", "startTime": "2024-02-15T14:25:52.0", "wktStepIndex": 7, "messageIndex": 14}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:29:32.0", "wktStepIndex": 8, "messageIndex": 15}, {"exercises": [{"category": "SHRUG", "name": "BARBELL_SHRUG", "probability": 100.0}], "duration": 335.055, "repetitionCount": 10, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:31:02.0", "wktStepIndex": 10, "messageIndex": 16}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:36:37.0", "wktStepIndex": 11, "messageIndex": 17}, {"exercises": [{"category": "SHRUG", "name": "BARBELL_SHRUG", "probability": 100.0}], "duration": 112.418, "repetitionCount": 2, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:38:07.0", "wktStepIndex": 10, "messageIndex": 18}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:39:59.0", "wktStepIndex": 11, "messageIndex": 19}, {"exercises": [{"category": "SHRUG", "name": "BARBELL_SHRUG", "probability": 100.0}], "duration": 137.247, "repetitionCount": 3, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:41:29.0", "wktStepIndex": 10, "messageIndex": 20}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:43:46.0", "wktStepIndex": 11, "messageIndex": 21}, {"exercises": [{"category": "FLYE", "name": "DUMBBELL_FLYE", "probability": 100.0}], "duration": 304.408, "repetitionCount": 7, "weight": 15875.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:45:16.0", "wktStepIndex": 13, "messageIndex": 22}, {"exercises": [], "duration": 60.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:50:21.0", "wktStepIndex": 14, "messageIndex": 23}, {"exercises": [{"category": "FLYE", "name": "DUMBBELL_FLYE", "probability": 100.0}], "duration": 188.738, "repetitionCount": 4, "weight": 15875.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:51:21.0", "wktStepIndex": 13, "messageIndex": 24}, {"exercises": [], "duration": 10.381, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:54:29.0", "wktStepIndex": 14, "messageIndex": 25}, {"exercises": [{"category": "FLYE", "name": "DUMBBELL_FLYE", "probability": 100.0}], "duration": 142.55, "repetitionCount": 4, "weight": 15875.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:54:40.0", "wktStepIndex": 13, "messageIndex": 26}, {"exercises": [], "duration": 60.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:57:02.0", "wktStepIndex": 14, "messageIndex": 27}, {"exercises": [{"category": "CURL", "name": "DUMBBELL_BICEPS_CURL", "probability": 100.0}], "duration": 233.782, "repetitionCount": 5, "weight": 18125.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:58:03.0", "wktStepIndex": 16, "messageIndex": 28}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:01:56.0", "wktStepIndex": 17, "messageIndex": 29}, {"exercises": [{"category": "CURL", "name": "DUMBBELL_BICEPS_CURL", "probability": 100.0}], "duration": 168.787, "repetitionCount": 7, "weight": 18125.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:03:26.0", "wktStepIndex": 16, "messageIndex": 30}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:06:15.0", "wktStepIndex": 17, "messageIndex": 31}, {"exercises": [{"category": "CURL", "name": "DUMBBELL_BICEPS_CURL", "probability": 100.0}], "duration": 80.746, "repetitionCount": 3, "weight": 18125.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:07:45.0", "wktStepIndex": 16, "messageIndex": 32}, {"exercises": [], "duration": 137.668, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:09:06.0", "wktStepIndex": 17, "messageIndex": 33}, {"exercises": [{"category": "ROW", "name": "BENT_OVER_ROW_WITH_BARBELL", "probability": 100.0}], "duration": 138.44, "repetitionCount": 2, "weight": 83937.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:11:23.0", "wktStepIndex": false, "messageIndex": 35}, {"exercises": [], "duration": 216.267, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:13:42.0", "wktStepIndex": false, "messageIndex": 36}, {"exercises": [{"category": "ROW", "name": "BENT_OVER_ROW_WITH_BARBELL", "probability": 100.0}], "duration": 128.323, "repetitionCount": 6, "weight": 61250.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:17:18.0", "wktStepIndex": false, "messageIndex": 37}, {"exercises": [], "duration": 163.336, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:19:27.0", "wktStepIndex": false, "messageIndex": 38}, {"exercises": [{"category": "ROW", "name": "BENT_OVER_ROW_WITH_BARBELL", "probability": 100.0}], "duration": 61.06, "repetitionCount": 6, "weight": 61250.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:22:10.0", "wktStepIndex": false, "messageIndex": 39}, {"exercises": [], "duration": 15.818, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:23:11.0", "wktStepIndex": false, "messageIndex": 40}]}

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
dump_data(data_dict, TEST_DATAFILE, 'w')
loaded_data = load_data(TEST_DATAFILE)

loaded_data == workouts
