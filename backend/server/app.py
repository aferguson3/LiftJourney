import logging

from flask import render_template

from backend.server import app, db
from backend.server.routes.database import database_bp
from backend.server.routes.service import service_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def register_blueprints():
    app.register_blueprint(database_bp)
    app.register_blueprint(service_bp)


@app.route("/")
def hello():
    return "Hello, world!"


@app.errorhandler(404)
def not_found(*args, **kwargs):
    return render_template('not_found.html', msg="Not Found"), 404


def main():
    with app.app_context():
        db.create_all()
    register_blueprints()
    app.run()


if __name__ == '__main__':
    main()
