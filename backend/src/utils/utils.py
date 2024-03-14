import logging
import time
from collections.abc import Callable
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def set_params_by_weeks(weeks_of_workouts: int, limit: int, start: int, startDate: str | date):
    params = {
        "startDate": str(startDate),
        "endDate": date.fromisoformat(startDate) + timedelta(days=7 * weeks_of_workouts),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }
    return params


def set_params_by_limit(limit: int, start: int, startDate: str | date = '2023-03-08'):
    params = {
        "startDate": str(startDate),
        "endDate": date.today(),
        "start": start,
        "limit": str(limit),
        "activityType": "fitness_equipment"
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
