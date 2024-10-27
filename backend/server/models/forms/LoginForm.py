from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange, InputRequired


class LoginForm(FlaskForm):
    email = StringField(
        "email",
        validators=[
            DataRequired(),
            Email("Invalid email address!"),
        ],
    )
    password = PasswordField("password", validators=[InputRequired()])


class MFAForm(FlaskForm):
    mfa_code = IntegerField(
        "MFA Code", validators=[InputRequired(), NumberRange(max=6)]
    )
