import logging

from backend.src import show_graph
from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.garmin_interaction import client_auth, get_activities, fill_out_workouts, get_workouts
from backend.src.utils import set_params_by_weeks

DATA_FILEPATH = "./data/workout_data.json"
METADATA_FILEPATH = './data/workout_metadata.json'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


# TODO: make all options chosen at runtime
# TODO: plot progress for all exercises given a workout type
# TODO: when editing exercises, exercise names are inconsistently saved


def main():
    client_auth()
    startDate = '2024-01-01'
    weeks_of_workouts = 20

    params = set_params_by_weeks(weeks_of_workouts, startDate)
    metadata = {"numWorkouts": "", "filepath": METADATA_FILEPATH,
                "dates": {"firstWorkout": "", "lastWorkout": ""},
                }
    menu = ("1: Fresh data & backup\n"
            "2: Fresh data & no backup\n"
            "3: Loaded data & no backup\n"
            "Choose an option: ")

    while True:
        match input(menu):
            case "1":  # Fresh data & backup
                IDs, dates = get_activities(params)
                workouts = get_workouts(IDs, dates)
                workouts_with_reps = fill_out_workouts(workouts)
                sorted_workouts = Manager.sort_workouts(workouts_with_reps, "datetime")
                Manager.dump_to_json(Manager.workouts_to_dict(sorted_workouts), DATA_FILEPATH, "w", metadata)
                Manager.list_incomplete_workouts(sorted_workouts)
                break
            case "2":  # Fresh data & no backup
                IDs, dates = get_activities(params)
                workouts = get_workouts(IDs, dates)
                workouts_with_reps = fill_out_workouts(workouts)
                sorted_workouts = Manager.sort_workouts(workouts_with_reps, "datetime")
                Manager.list_incomplete_workouts(sorted_workouts)
                break
            case "3":  # Loaded data & no backup
                workouts = Manager.load_workouts(DATA_FILEPATH)
                sorted_workouts = Manager.sort_workouts(workouts, "datetime")
                Manager.list_incomplete_workouts(sorted_workouts)
                break
            case _:
                pass

    logger.info(
        f"Num of workouts: {len(sorted_workouts)}, Workout 0: {sorted_workouts[0].name} {sorted_workouts[0].version}"
        f"\n\tset 3: {sorted_workouts[0].view_sets()[3]}")

    show_graph(sorted_workouts)


if __name__ == "__main__":
    main()
