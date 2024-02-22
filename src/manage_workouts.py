import json
import logging

from src.models.ExerciseSet import ExerciseSet
from src.models.Workout import Workout

logger = logging.getLogger(__name__)


def workouts_to_dict(data: list[Workout]) -> dict:
    workouts = list()
    for workout in data:
        workout.validation_check()
        workouts.append(workout.asdict())
    return {"workouts": workouts}


def dump_to_json(data: dict, filepath: str, option):
    match option:
        case "a" | "w":
            try:
                with open(filepath, option) as file:
                    json.dump(data, file, sort_keys=True)
            except FileNotFoundError as e:
                logger.error(f"{filepath} not found.")
            except TypeError as e:
                logger.error(f"{e} Check data's type.")
        case _:
            raise ValueError(f"Invalid option:{option} used in json.dump().")


def load_workouts(filepath: str) -> list[Workout]:
    try:
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            all_workouts = list()
            for workout in json_data["workouts"]:
                a_workout = Workout()
                a_workout.init_workout(workout)
                all_workouts.append(a_workout)
        return all_workouts

    except FileNotFoundError as e:
        logger.error(f"{e}")


def sort_workouts(input_data: Workout | list[Workout], key: str, reverse=False) \
        -> list[Workout] | list[ExerciseSet] | None:
    searchedData, isValidKey = None, None
    if isinstance(input_data, list):
        isValidKey = hasattr(input_data[0], key)
        searchedData = input_data
    elif isinstance(input_data, Workout):
        isValidKey = hasattr(input_data.sets[0], key)
        searchedData = input_data.sets

    if isValidKey:
        try:
            sorted_list = sorted(searchedData, key=lambda w: getattr(w, key), reverse=reverse)
            return sorted_list
        except TypeError as msg:
            logger.error(f"{msg}")

    else:
        logger.error(f"Sorting {type(input_data)} by key: {key} FAILED.")

    return None
