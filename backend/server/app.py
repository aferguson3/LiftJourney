from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from backend.server.config.config import app_config_selection, db, cache, db_config
from backend.server.routes import *
from backend.src import load_garmin_client


def register_blueprints(app_: Flask):
    app_.register_blueprint(database_bp)
    app_.register_blueprint(service_bp)
    app_.register_blueprint(admin_bp)
    app_.register_blueprint(login_bp)
    app_.register_blueprint(statues_bp)


def create_app(
    db_: SQLAlchemy = db, cache_: Cache = cache, app_config: str | None = None
):
    """
    :param db_:
    :param cache_:
    :param app_config: "base", "debug", or "prod". Default: "base"
    :return:
    """

    app_config = app_config_selection(app_config)
    curr_app = Flask(__name__)
    curr_app.config.from_object(app_config)

    if curr_app.config["DEBUG"] is True:
        DebugToolbarExtension(curr_app)
    cache_.init_app(curr_app)
    db_.init_app(curr_app)

    with curr_app.app_context():
        db_config(db_, curr_app)
    # cache.clear()
    load_garmin_client()
    register_blueprints(curr_app)

    return curr_app


if __name__ == "__main__":
    create_app(db, cache, app_config="debug")
