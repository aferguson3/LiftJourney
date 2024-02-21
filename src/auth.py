import logging
import os

import garth
from dotenv import dotenv_values

# Assumes Garmin connect user/pass are saved in .env file
logger = logging.getLogger(__name__)


def client_auth():
    try:
        garth.resume("../creds")
        logger.info("0Auth tokens found. Login successful.")
    except FileNotFoundError:
        if not os.path.exists("../creds"):
            os.mkdir("../creds")
        config = dotenv_values("../.env")
        garth.login(config["EMAIL"], config["PASSWORD"])
        garth.save("../creds")
