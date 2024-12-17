import logging
import pathlib
import time
from collections.abc import Callable
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def set_params_by_weeks(
    weeks_of_workouts: int, start_date: str | date, start: int = 0, limit: int = 999
):
    start_date = str(start_date)
    _endDate = date.fromisoformat(start_date) + timedelta(days=7 * weeks_of_workouts)
    endDate = (
        str(_endDate) if _endDate <= date.today() else str(date.today().isoformat())
    )
    params = {
        "startDate": start_date,
        "endDate": endDate,
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment",
    }
    return params


def set_params_by_limit(
    limit: int, start: int = 0, start_date: str | date = "2023-03-08"
):
    params = {
        "startDate": str(start_date),
        "endDate": date.today(),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment",
    }
    return params


def timer(func: Callable[..., ...]):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} took {end - start:.02f}s")
        return result

    return wrapper


def filepath_validation(filepath: str):
    if not isinstance(filepath, str):
        raise TypeError(f"{filepath} is invalid filepath.")
    if not pathlib.Path(filepath).is_file():
        raise FileNotFoundError(f"{filepath} was not found.")
