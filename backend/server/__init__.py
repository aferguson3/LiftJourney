import pathlib

APP_DIRECTORY = pathlib.Path(__file__).parent.resolve()
WORKING_DIR = APP_DIRECTORY.parents[1]
ENV_PATH = WORKING_DIR / ".env"
