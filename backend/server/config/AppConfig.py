import logging
import pathlib
import uuid
from enum import Enum

from backend.server import APP_DIRECTORY

DB_URI = "sqlite:///" + str(pathlib.Path("data", "workouts.db"))
IN_MEMORY_DB = "sqlite:///:memory:"
TEST_URI = "sqlite:///" + str(pathlib.Path("data", "test_workouts.db"))
ENV_PATH = APP_DIRECTORY.parents[1] / ".env"


class ValidURITypes(Enum):
    IN_MEMORY_DB = 1
    TEST_DB = 2
    MAIN_DB = 3


logger = logging.getLogger(__name__)


def _db_uri_selection(uri_type: str):
    """
    :param uri_type: Options: IN_MEMORY_DB, TEST_DB, or MAIN_DB
    :type uri_type: str
    :return: Sqlalchemy Database URI
    """

    if isinstance(uri_type, str):
        match uri_type.upper():
            case ValidURITypes.IN_MEMORY_DB.name:
                selected_URI = IN_MEMORY_DB
            case ValidURITypes.TEST_DB.name:
                selected_URI = TEST_URI
            case ValidURITypes.MAIN_DB.name:
                selected_URI = DB_URI
            case _:
                raise RuntimeError(f"Invalid URI Type: '{uri_type}' was used.")

        return selected_URI
    else:
        logger.debug(f"{uri_type} is not str type")


def _default_uri_type(uri_type: str, default_uri: str):
    if not isinstance(uri_type, str) and uri_type is not None:
        raise ValueError(f"{uri_type} is not type str")

    return uri_type if uri_type is not None else default_uri


class AppConfig(object):
    SECRET_KEY = uuid.uuid4().hex

    def __init__(self, uri_type: str = None, custom_uri: str = None):
        """
        :param uri_type: Uses the SQLAlchemy DB URI defined by the provided key. Default ``MAIN_DB``
        :type uri_type: str
        """

        self.uri_type = _default_uri_type(uri_type, "MAIN_DB")
        self._SQLALCHEMY_DATABASE_URI = (
            _db_uri_selection(self.uri_type) if custom_uri is None else custom_uri
        )

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self._SQLALCHEMY_DATABASE_URI

    @SQLALCHEMY_DATABASE_URI.setter
    def SQLALCHEMY_DATABASE_URI(self, custom_uri: str = None):
        if custom_uri is not None:
            self._SQLALCHEMY_DATABASE_URI = custom_uri
        else:
            self._SQLALCHEMY_DATABASE_URI = _db_uri_selection(self.uri_type)


class DebugConfig(AppConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    def __init__(self, uri_type=None, custom_uri: str = None):
        self.uri_type = _default_uri_type(uri_type, "TEST_DB")
        super().__init__(self.uri_type, custom_uri)


class ProdConfig(AppConfig):
    DEBUG = False


class TestConfig(AppConfig):
    WTF_CSRF_ENABLED = False
    TESTING = True

    def __init__(self, uri_type=None, custom_uri: str = None):
        self.uri_type = _default_uri_type(uri_type, "IN_MEMORY_DB")
        super().__init__(self.uri_type, custom_uri)
