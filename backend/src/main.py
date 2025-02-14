import datetime
import logging
import pathlib

from backend.src import show_graph
from backend.src.garmin_interaction import load_garmin_from_env, run_service
from backend.src.utils import set_params_by_weeks

DATA_FILEPATH = str(pathlib.Path("./data/workout_data.json").resolve())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.ERROR)


def main():
    load_garmin_from_env()
    endDate = datetime.date.today()
    weeks_of_workouts = 10

    params = set_params_by_weeks(weeks_of_workouts, endDate)
    menu = (
        "1: Fresh data & backup\n"
        "2: Fresh data & no backup\n"
        "3: Loaded data & no backup\n"
        "Choose an option: "
    )
    while True:
        match input(menu):
            case "1":  # Fresh data & backup
                workouts = run_service(params, backup=True, filepath=DATA_FILEPATH)
                break
            case "2":  # Fresh data & no backup
                workouts = run_service(params)
                break
            case "3":  # Loaded data & no backup
                workouts = run_service(params, load=True, filepath=DATA_FILEPATH)
                break
            case _:
                pass

    while True:
        menu = (
            "---------------------------------------\n"
            "1. View a progression graph\n"
            "2. Close Program\n"
            "---------------------------------------\n"
            "Choose an option: "
        )
        match (input(menu)):
            case "1":
                show_graph(workouts)
                print("Displaying workout graph.")
                continue
            case "2":
                exit(0)
            case _:
                continue


if __name__ == "__main__":
    main()
