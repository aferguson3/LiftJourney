import logging
import pathlib
import time
from collections.abc import Callable
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def set_params_by_weeks(
    weeks_of_workouts: int, end_date: str | date, start: int = 0, limit: int = 999
):
    end_date = str(end_date)
    start_date = date.fromisoformat(end_date) - timedelta(days=7 * weeks_of_workouts)
    start_date = (
        str(start_date) if start_date <= date.today() else str(date.today().isoformat())
    )
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment",
    }
    return params


def set_params_by_date(
    start_date: str,
    end_date: str | date = None,
    start: int = 0,
):
    if date.fromisoformat(str(start_date)) > date.today():
        start_date = date.today()

    if end_date is None:
        end_date = date.today()
    elif date.fromisoformat(str(end_date)) > date.today():
        end_date = date.today()

    params = {
        "startDate": str(start_date),
        "endDate": str(end_date),
        "start": start,
        "limit": 999,
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
