from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'
db = SQLAlchemy(app)

app.debug = True
app.config['SECRET_KEY'] = "Dice_gaming"
toolbar = DebugToolbarExtension(app)
