import logging
import pathlib
from enum import Enum

from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from backend.server import APP_DIRECTORY
from backend.server.config.AppConfig import (
    AppConfig,
    DebugConfig,
    ProdConfig,
    TestConfig,
)


class FlaskConfigs(Enum):
    BASE = 1
    DEBUG = 2
    PROD = 3
    TEST = 4


db = SQLAlchemy()
cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_THRESHOLD": 20,
        "CACHE_DEFAULT_TIMEOUT": 250,
    }
)
logger = logging.getLogger(__name__)


def db_config(db_, app_):
    try:
        db_dir = APP_DIRECTORY / "data"
        if not db_dir.exists():
            db_dir.mkdir(parents=True)

        db_.create_all()
        logger.info(
            f"DB Name: {pathlib.Path(app_.config.get('SQLALCHEMY_DATABASE_URI')).name}"
        )
    except OperationalError:
        raise FileNotFoundError(
            f"Unable to open DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}"
        )


def app_config_selection(app_config: str = None, **kwargs) -> AppConfig:
    if app_config is None:
        curr_config = AppConfig(**kwargs)
        logger.info(f"App Config: {type(curr_config)}")
        return curr_config

    if not isinstance(app_config, str):
        raise TypeError(f"Invalid app_config: {app_config}")

    match app_config.upper():
        case FlaskConfigs.BASE.name:
            curr_config = AppConfig(**kwargs)
            LOGGING_LEVEL = logging.WARN
        case FlaskConfigs.DEBUG.name:
            curr_config = DebugConfig(**kwargs)
            LOGGING_LEVEL = logging.DEBUG
        case FlaskConfigs.PROD.name:
            curr_config = ProdConfig(**kwargs)
            LOGGING_LEVEL = logging.WARN
        case FlaskConfigs.TEST.name:
            curr_config = TestConfig(**kwargs)
            LOGGING_LEVEL = logging.DEBUG
        case _:
            curr_config = AppConfig(**kwargs)
            LOGGING_LEVEL = logging.WARN

    logging.basicConfig(level=LOGGING_LEVEL)
    logger.info(f"App Config: {type(curr_config)}")
    return curr_config
