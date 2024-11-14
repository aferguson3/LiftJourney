import logging

from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from backend.server.config.BaseConfig import (
    BaseConfig,
    DebugConfig,
    ProdConfig,
    TestConfig,
)

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
        db_.create_all()
        logger.info(f"DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}")
    except OperationalError:
        raise FileNotFoundError(
            f"Unable to open DB URI: {app_.config.get('SQLALCHEMY_DATABASE_URI')}"
        )


def app_config_selection(selection: str = None, **kwargs) -> BaseConfig:
    if selection is None:
        curr_config = BaseConfig()
        logger.info(f"App Config: {type(curr_config)}")
        return curr_config

    if not isinstance(selection, str):
        raise TypeError(f"Invalid app_config: {selection}")

    match selection.upper():
        case "BASE":
            curr_config = BaseConfig(**kwargs)
            LOGGING_LEVEL = logging.WARN
        case "DEBUG":
            curr_config = DebugConfig(**kwargs)
            LOGGING_LEVEL = logging.DEBUG
        case "PROD":
            curr_config = ProdConfig(**kwargs)
            LOGGING_LEVEL = logging.WARN
        case "TEST":
            curr_config = TestConfig(**kwargs)
            LOGGING_LEVEL = logging.DEBUG
        case _:
            curr_config = BaseConfig(**kwargs)
            LOGGING_LEVEL = logging.WARN

    logging.basicConfig(level=LOGGING_LEVEL)
    logger.info(f"App Config: {type(curr_config)}")
    return curr_config
