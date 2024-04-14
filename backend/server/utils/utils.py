import logging
from datetime import datetime
from io import StringIO
from typing import Tuple

import pandas
import pandas as pd
from flask import session
from sqlalchemy import select, update

from backend.server import db
from backend.server.models import ExerciseSetDB, WorkoutDB

logger = logging.getLogger(__name__)


def remove_from_session(key: str):
    if key in session:
        session.__delitem__(key)


def _get_dataframe_index() -> list[Tuple]:
    index_2d: list[Tuple] = []
    workout_ids = db.session.execute(
        select(ExerciseSetDB.workout_id)
    ).scalars().unique().all()

    for cur_workout_id in workout_ids:
        cur_workout_date = db.session.execute(
            select(WorkoutDB.datetime).where(WorkoutDB.id == int(cur_workout_id))
        ).scalar()
        cur_sets = db.session.execute(
            select(ExerciseSetDB).where(ExerciseSetDB.workout_id == int(cur_workout_id))
        ).all()
        cur_workout_date = datetime.fromisoformat(cur_workout_date).date().strftime("%m/%d/%y")
        for cur_set_number in list(range(1, len(cur_sets) + 1)):
            index_2d.append((cur_workout_date, cur_set_number))

        db.session.execute(  # TODO: only update when empty
            update(ExerciseSetDB)
            .where(ExerciseSetDB.workout_id == int(cur_workout_id))
            .values(date=cur_workout_date)
        )
        db.session.commit()
    return index_2d


def get_dataframe() -> pandas.DataFrame:
    sets_df = session.get('df')
    if sets_df is None:
        sets_df = pd.read_sql("exercise_sets", db.session.connection(),
                              parse_dates={"startTime": "%H:%M:%S", "date": "%m/%d/%y"})
        index_df = pd.MultiIndex.from_tuples(_get_dataframe_index(), names=["Dates", "Sets"])
        sets_df.set_index(index_df, inplace=True)
        session['df'] = sets_df.to_json()
    else:
        sets_df = pd.read_json(StringIO(sets_df), convert_dates=True)
        sets_df["date_str"] = sets_df["date"].dt.strftime("%m/%d/%y")
    return sets_df
