import logging

from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from backend.server.config.BaseConfig import BaseConfig, DebugConfig, ProdConfig

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


def app_config_selection(selection: str) -> BaseConfig:
    if selection is None:
        return BaseConfig()

    if not isinstance(selection, str):
        raise TypeError(f"Invalid app_config: {selection}")

    match selection.upper():
        case "BASE":
            return BaseConfig()
        case "DEBUG":
            return DebugConfig()
        case "PROD":
            return ProdConfig()
        case _:
            return BaseConfig()
