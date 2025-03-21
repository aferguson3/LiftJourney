import logging

from sqlalchemy import select, update

from backend.server.config import db, cache
from backend.server.models import Workout
from backend.server.models import WorkoutDB, MuscleMapDB

logger = logging.getLogger(__name__)


def _isNewWorkoutEntry(entry: WorkoutDB) -> bool:
    result = (
        db.session.execute(
            select(WorkoutDB).where(WorkoutDB.activityId == int(entry.activityId))
        )
        .scalars()
        .first()
    )
    return result is None


def _isNewExerciseEntry(entry: MuscleMapDB) -> bool:
    result = (
        db.session.execute(
            select(MuscleMapDB.exerciseName).where(
                MuscleMapDB.exerciseName is str(entry.exerciseName)
            )
        )
        .scalars()
        .first()
    )
    return result is None


def invalidate_cache(keys: list[str] = None):
    caches_keys = {"sets_df", "exercise_info"}
    keys_to_remove = caches_keys
    if keys is not None:
        keys_to_remove = caches_keys.intersection(set(keys))

    for key in keys_to_remove:
        cache.delete(key)
        logger.info(f"Cache: {key} was deleted.")


def add_workouts(workouts: list[Workout]):
    if not isinstance(workouts[0], Workout):
        raise ValueError(f"{type(workouts[0])} is not type Workout")
    reset_cache = False
    workoutsDB = WorkoutDB.list_to_workoutsDB(workouts)

    for wo in workoutsDB:
        if not _isNewWorkoutEntry(wo) or wo.category == "UNTRACKED":
            continue
        reset_cache = True
        db.session.add(wo)
    if reset_cache:
        invalidate_cache(["sets_df", "exercise_info"])
    db.session.commit()


def add_mappings(values: list[MuscleMapDB]):
    for exercise in values:
        if not _isNewExerciseEntry(exercise):
            continue
        db.session.add(exercise)
    db.session.commit()


def select_mappings() -> list[MuscleMapDB]:
    return (db.session.execute(select(MuscleMapDB))).scalars().all()


def select_activityIDs() -> list[int]:
    return (db.session.execute(select(WorkoutDB.activityId))).scalars().all()


def select_datetimes() -> list[int]:
    return (db.session.execute(select(WorkoutDB.datetime))).scalars().all()


def update_mappings(new_entries: list[MuscleMapDB] | dict):
    if new_entries is None or len(new_entries) == 0:
        return

    if isinstance(new_entries, list):
        for value in new_entries:
            # noinspection PyTypeChecker
            db.session.execute(
                update(MuscleMapDB)
                .where(MuscleMapDB.exerciseName == value.exerciseName)
                .values(category=f"{value.category}")
            )
    elif isinstance(new_entries, dict):
        for exercise_name, category in new_entries.items():
            # noinspection PyTypeChecker
            db.session.execute(
                update(MuscleMapDB)
                .where(MuscleMapDB.exerciseName == exercise_name)
                .values(category=f"{category}")
            )
    else:
        logger.debug(f"TypeError: {new_entries} is not of type list, dict.")
        return

    invalidate_cache(["exercise_info"])
    db.session.commit()
