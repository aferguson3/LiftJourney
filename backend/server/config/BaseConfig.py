import logging
import uuid
from enum import Enum

from backend.server import APP_DIRECTORY

DB_URI = "sqlite:///" + str(APP_DIRECTORY / "data" / "workouts.db")
IN_MEMORY_DB = "sqlite:///:memory:"
TEST_URI = "sqlite:///" + str(APP_DIRECTORY / "data" / "test_workouts.db")
ENV_PATH = APP_DIRECTORY.parents[1] / ".env"

logger = logging.getLogger(__name__)


class ValidURITypes(Enum):
    IN_MEMORY_DB = 1
    TEST_DB = 2
    MAIN_DB = 3


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
                raise RuntimeError(f"Invalid DB URI: {uri_type} was used.")

        print(uri_type)
        return selected_URI
    else:
        logger.debug(f"{uri_type} is not str type")


def _default_uri_type(uri_type: str, default_uri: str):
    if not isinstance(uri_type, str) and uri_type is not None:
        raise ValueError(f"{uri_type} is not type str")

    return uri_type if uri_type is not None else default_uri


class BaseConfig(object):
    SECRET_KEY = uuid.uuid4().hex

    def __init__(self, uri_type: str = None, custom_uri=None):
        """
        :param uri_type: Options: IN_MEMORY_DB, TEST_DB, or MAIN_DB
        :type uri_type: str
        """

        self.uri_type = _default_uri_type(uri_type, "MAIN_DB")
        self._SQLALCHEMY_DATABASE_URI = _db_uri_selection(self.uri_type)

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self._SQLALCHEMY_DATABASE_URI

    @SQLALCHEMY_DATABASE_URI.setter
    def SQLALCHEMY_DATABASE_URI(self, custom_uri: str = None):
        if custom_uri is not None:
            self._SQLALCHEMY_DATABASE_URI = custom_uri
        else:
            self._SQLALCHEMY_DATABASE_URI = _db_uri_selection(self.uri_type)


class DebugConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    def __init__(self, uri_type=None):
        self.uri_type = _default_uri_type(uri_type, "TEST_DB")
        super().__init__(self.uri_type)


class ProdConfig(BaseConfig):
    DEBUG = False


class TestConfig(BaseConfig):
    WTF_CSRF_ENABLED = False
    TESTING = True

    def __init__(self, uri_type=None):
        self.uri_type = _default_uri_type(uri_type, "IN_MEMORY_DB")
        super().__init__(self.uri_type)
