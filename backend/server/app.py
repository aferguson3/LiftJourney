import logging

from flask import render_template

from backend.server import app, db, cache
from backend.server.routes.admin import admin_bp
from backend.server.routes.database import database_bp
from backend.server.routes.service import service_bp
from backend.src import client_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def register_blueprints():
    app.register_blueprint(database_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(admin_bp)


@app.route("/")
def hello():
    return "Hello, world!"


@app.errorhandler(404)
def not_found(*args, **kwargs):
    return render_template("not_found.html", msg="Not Found"), 404


def main():
    with app.app_context():
        db.create_all()
        logger.info(f"DB URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    client_auth()
    register_blueprints()
    cache.clear()
    app.run()


if __name__ == "__main__":
    main()
