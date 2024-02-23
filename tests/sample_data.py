from src.models.Workout import Workout
from src.models.ExerciseSet import ExerciseSet

wo1 = Workout()
wo1.activityId = 77789374356
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
                startTime="2024-02-16T14:23:38.0")]
wo1.sets = sets1

wo2 = Workout()
wo2.activityId = 22944539762
wo2.datetime = "2024-02-13T13:19:35.0"
sets2 = [ExerciseSet(exerciseName="BARBELL_BENCH_PRESS", numReps=17, weight_grams=61250.0, duration_secs=150.134,
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
         ExerciseSet(exerciseName=None, numReps=7, weight_grams=13625.0, duration_secs=125.879, stepIndex=16,
                     startTime="2024-02-13T14:16:04.0"),
         ExerciseSet(exerciseName=None, numReps=3, weight_grams=13625.0, duration_secs=100.188, stepIndex=16,
                     startTime="2024-02-13T14:19:40.0"),
         ExerciseSet(exerciseName=None, numReps=2, weight_grams=13625.0, duration_secs=150.757, stepIndex=16,
                     startTime="2024-02-13T14:22:31.0")]
wo2.sets = sets2

wo3 = Workout()
wo3.activityId = 10297505921
wo3.datetime = "2024-02-15T13:31:41.0"
sets3 = [
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
                startTime="2024-02-15T14:41:29.0")]
wo3.sets = sets3