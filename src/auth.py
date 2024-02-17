import logging
import os

import garth
from dotenv import dotenv_values


# Assumes Garmin connect user/pass are saved in .env file


def client_auth():
    try:
        garth.resume("../creds")
        logging.info("0Auth tokens found. Login successful.")
    except FileNotFoundError:
        if not os.path.exists("../creds"):
            os.mkdir("../creds")
        config = dotenv_values("../.env")
        garth.login(config["EMAIL"], config["PASSWORD"])
        garth.save("../creds")
