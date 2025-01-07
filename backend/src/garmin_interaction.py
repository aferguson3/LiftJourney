import logging
import multiprocessing
import pathlib
import queue
import re
from datetime import datetime, timedelta
from threading import Thread
from typing import Tuple

import garth
from dotenv import dotenv_values
from garth.exc import GarthException

from backend.server import WORKING_DIR, ENV_PATH
from backend.src.WorkoutManagement import WorkoutManagement as Manager
from backend.src.models import Workout, ExerciseSet
from backend.src.utils import Endpoints
from backend.src.utils.utils import timer, filepath_validation

logger = logging.getLogger(__name__)
Queue_ = queue.Queue()
MAX_THREADS = multiprocessing.cpu_count()
NUM_THREADS = 6
NUM_THREADS = NUM_THREADS if MAX_THREADS >= NUM_THREADS else multiprocessing.cpu_count()
CREDS_PATH = WORKING_DIR / "backend" / "creds"


# Assumes Garmin connect user/pass are saved in .env file
def load_garmin_from_env():
    try:
        garth.resume(str(CREDS_PATH))
        logger.info("0Auth tokens found. Login successful.")
    except FileNotFoundError:
        if not pathlib.Path.exists(CREDS_PATH):
            pathlib.Path.mkdir(CREDS_PATH)
        config = dotenv_values(str(ENV_PATH))
        garth.login(config["EMAIL"], config["PASSWORD"])
        garth.save(str(CREDS_PATH))


def is_oauth_tokens_active():
    return (
        garth.client.oauth1_token is not None and garth.client.oauth2_token is not None
    )


def load_oauth_tokens(filepath=None) -> bool:
    """
    Attempts to load Garmin OAuth Tokens or creates a directory to store tokens, if the ``filepath`` doesnt already exist.
    :param filepath:
    :return:
    """
    filepath_ = filepath if filepath is not None else CREDS_PATH
    try:
        garth.resume(str(filepath_))
        logger.info("0Auth tokens found. Login successful.")
        return True
    except FileNotFoundError:
        if not pathlib.Path.exists(filepath_):
            pathlib.Path.mkdir(filepath_)
            logger.info(f"No OAuth Tokens found.")
        return False


# Gathers all fitness activities by date
@timer
def get_activities(params: dict) -> Tuple[list[int] | None, list[str] | None]:
    try:
        activity_data: dict = garth.connectapi(
            f"{Endpoints.garmin_connect_activities}", params=params
        )
    except GarthException as e:
        logger.debug(e.error)
        return None, None

    activityIds, removedIds = list(), list()
    activityDatetimes = list()

    for activity in activity_data:
        if _is_unwanted_activity(activity):
            removedIds.append(activity["activityId"])
            continue
        activityIds.append(activity["activityId"])
        activityDatetimes.append(activity["startTimeLocal"])
    logger.debug(
        f"Max limit for Ids: {params['limit']}, Number of Removed Ids: {len(removedIds)}, Number of Ids: {len(activityIds)}"
        f"\n{activityIds[:5]} ..."
    )
    return activityIds, activityDatetimes


def _is_unwanted_activity(activity: dict) -> bool:
    return (
        str(activity["activityName"]).find("Pickup") > -1
        or str(activity["activityName"]).find("Basketball") > -1
    )


@timer
def get_workouts(
    activityIds: list, activityDatetimes: list, stored_IDs: list[int] = None
) -> list[Workout]:
    threads = []
    if stored_IDs is not None:
        activityIds_ = set(activityIds).difference(stored_IDs)
    else:
        activityIds_ = activityIds

    splice = int(len(activityIds_) / NUM_THREADS)
    workouts_rv = []

    if len(activityIds_) < NUM_THREADS:
        for ID, _datetime in zip(activityIds_, activityDatetimes):
            t = Thread(target=_get_workouts, args=(activityDatetimes, ID))
            t.start()
            threads.append(t)
    else:
        for i in range(0, NUM_THREADS):
            cur_index = i * splice
            t = Thread(
                target=_get_workouts,
                args=(
                    activityDatetimes[cur_index : cur_index + splice],
                    activityIds_[cur_index : cur_index + splice],
                ),
            )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    while not Queue_.empty():
        workouts_rv = workouts_rv + Queue_.get()
    return workouts_rv


def _get_workouts(activityDatetimes: list, activityIds: list | int) -> None:
    totalWorkouts = list()  # most recent workouts stored first
    if isinstance(activityDatetimes, str):
        activityDatetimes = [activityDatetimes]
    if isinstance(activityIds, int):
        activityIds = [activityIds]

    for Id, _datetime in zip(activityIds, activityDatetimes):
        try:
            data = garth.connectapi(
                f"{Endpoints.garmin_connect_activity}/{Id}/exerciseSets"
            )
        except GarthException as e:
            logger.debug(e.error)
            return
        a_workout = Workout()
        all_workout_sets = list()

        for currSet in data["exerciseSets"]:
            a_set = ExerciseSet()
            if currSet["setType"] == "REST":
                continue
            if currSet["exercises"][0]["category"] == "INDOOR_BIKE":
                continue
            if _isWarmupSet(currSet):
                # skip warmup sets
                logger.debug(
                    f"Skipped {currSet['exercises'][0]['name']}, weight: {currSet['weight']}"
                )
                continue
            currWeight = currSet["weight"] if currSet["weight"] is not None else 0
            curr_time = _format_set_time(currSet["startTime"], timedelta(hours=5))

            a_set.exerciseName = currSet["exercises"][0]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight = round(currWeight * 0.002204623)
            a_set.startTime = curr_time
            a_set.stepIndex = currSet["wktStepIndex"]
            all_workout_sets.append(a_set)

        a_workout.activityId = Id
        a_workout.datetime = _datetime
        a_workout.sets = all_workout_sets
        totalWorkouts.append(a_workout)
    Queue_.put(totalWorkouts)
    Queue_.task_done()


def _format_set_time(
    set_time: str | None, timedelta_from_Garmin: timedelta
) -> str | None:
    if set_time is None:
        return
    set_time = set_time.replace(".0", "")
    set_time_dt = datetime.fromisoformat(set_time)
    formatted_time = (set_time_dt - timedelta_from_Garmin).time().isoformat()
    return formatted_time


def _isWarmupSet(garmin_exercise_set: dict) -> bool:
    result = (
        garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BENCH_PRESS"
        and garmin_exercise_set["weight"] <= 61251
    )
    result = (
        result
        or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_BACK_SQUAT"
        and garmin_exercise_set["weight"] <= 61251
    )
    result = (
        result
        or garmin_exercise_set["exercises"][0]["name"] == "BARBELL_DEADLIFT"
        and garmin_exercise_set["weight"] <= 61251
    )
    return result


@timer
def fill_out_workouts(workouts: list[Workout]) -> list[Workout]:
    # Fills out targetReps and missing exerciseNames using scheduled workout info
    threads = []
    splice = int(len(workouts) / NUM_THREADS)
    workouts_rv = []

    if len(workouts) < NUM_THREADS:
        for wo in workouts:
            t = Thread(target=_fill_out_workouts, args=[wo])
            t.start()
            threads.append(t)
    else:
        for i in range(0, NUM_THREADS):
            cur_index = i * splice
            t = Thread(
                target=_fill_out_workouts,
                args=[workouts[cur_index : cur_index + splice]],
            )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    while not Queue_.empty():
        workouts_rv = workouts_rv + Queue_.get()

    return workouts_rv


def _fill_out_workouts(workouts: list[Workout] | Workout):
    if isinstance(workouts, Workout):
        workouts = [workouts]

    for wo in workouts:
        try:
            garmin_data = garth.connectapi(
                f"{Endpoints.garmin_connect_activity}/{wo.activityId}/workouts"
            )
        except GarthException as e:
            li
        if garmin_data is None:  # Checks workout data's present
            print(f"{wo.datetime}")
            continue
        garmin_data = garmin_data[0]
        wo = _get_workout_name(wo)

        for currSet in wo.sets:
            currStepIndex = currSet.stepIndex
            if currStepIndex is None:
                continue  # Ignores unscheduled exercises w/o stepIndex
            currSet.targetReps = int(
                garmin_data["steps"][currStepIndex]["durationValue"]
            )
            if currSet.exerciseName is None:
                newName = garmin_data["steps"][currStepIndex]["exerciseName"]
                newCategory = garmin_data["steps"][currStepIndex]["exerciseCategory"]
                currSet.exerciseName = newName if newName is not None else newCategory
    Queue_.put(workouts)
    Queue_.task_done()


def _get_workout_name(workout: Workout):
    pattern = r"\b\d+(?:\.\d+)+\b"
    try:
        garmin_data = garth.connectapi(
            f"{Endpoints.garmin_connect_activity}/{workout.activityId}"
        )
    except GarthException as e:
        logger.debug(e.error)
        return
    workout_name_str = garmin_data["activityName"]
    version_str = re.search(pattern, workout_name_str)
    version_str = version_str.group() if version_str is not None else None
    workout_name = re.sub(pattern, "", workout_name_str).strip()
    workout.version = version_str
    workout.name = workout_name
    return workout


def run_service(
    params: dict,
    backup: bool = False,
    load: bool = False,
    filepath: str = None,
    stored_IDs: list[int] = None,
) -> list[Workout] | None:
    workouts = list()
    match load:
        case True:
            filepath_validation(filepath)
            workouts = Manager.load_workouts(filepath)
            workouts = Manager.sort_workouts(workouts, "datetime")
        case False:
            IDs, dates = get_activities(params)
            workouts = get_workouts(IDs, dates, stored_IDs=stored_IDs)
            if len(workouts) == 0:
                return
            workouts = fill_out_workouts(workouts)
            workouts = Manager.sort_workouts(workouts, "datetime")
            workouts = _set_tracking_status(workouts)
    if backup:
        filepath_validation(filepath)
        Manager.dump_to_json(Manager.workouts_to_dict(workouts), filepath, "w")

    Manager.list_incomplete_workouts(workouts)
    logger.info(
        f"Num of workouts: {len(workouts)}, Workout 0: {workouts[0].name} {workouts[0].version} {workouts[0].category}"
        f"\n\tset 3: {workouts[0].view_sets()[3]}"
    )
    return workouts


def _set_tracking_status(workouts: list[Workout]) -> list[Workout]:
    # Determines what workouts are graphed
    for entry in workouts:
        if (
            entry.version is None
            or "LIGHT" in str(entry.name).upper()
            or "NOT HEAVY" in str(entry.name).upper()
            or "REST" in str(entry.name).upper()
        ):
            entry.category = "UNTRACKED"
        else:
            entry.category = "TRACKED"
    return workouts
