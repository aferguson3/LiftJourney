import pathlib

import dotenv
from cachelib import FileSystemCache
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

IN_MEMORY = False
SERVER_SESSION = True
DEBUG = True
# Flask-SQLite
app = Flask(__name__)
if IN_MEMORY is True:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
db = SQLAlchemy(app)

# Flask Session
if SERVER_SESSION is True:
    app.config['SESSION_TYPE'] = 'cachelib'
    app.config['SESSION_CACHELIB'] = FileSystemCache(threshold=10, cache_dir="flask_session")
    app.config['SESSION_PERMANENT'] = False
# Flask Debugger
if DEBUG is True:
    app.debug = True
    env_path = pathlib.Path.cwd().parent.parent / ".env"
    app.config['SECRET_KEY'] = dotenv.get_key(str(env_path), "SECRET_KEY")
    toolbar = DebugToolbarExtension(app)
