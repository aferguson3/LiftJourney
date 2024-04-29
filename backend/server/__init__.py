import pathlib

import dotenv
from cachelib import FileSystemCache
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

IN_MEMORY = False
SERVER_SESSION = True
DEBUG = True
BASEDIR = pathlib.Path.cwd()
DB_URI = 'sqlite:///' + str(BASEDIR.joinpath('workouts.db'))

# Flask-SQLite
app = Flask(__name__)
env_path = pathlib.Path.cwd().parent.parent / ".env"
app.config['SECRET_KEY'] = dotenv.get_key(str(env_path), "SECRET_KEY")

if IN_MEMORY is True:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

# Flask Session
if SERVER_SESSION is True:
    app.config['SESSION_TYPE'] = 'cachelib'
    app.config['SESSION_CACHELIB'] = FileSystemCache(threshold=10, cache_dir="flask_session")
    app.config['SESSION_PERMANENT'] = False
# Flask-Toolbar Debugger
if DEBUG is True:
    app.debug = True
    toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
