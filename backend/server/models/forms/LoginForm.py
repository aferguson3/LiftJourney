from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, InputRequired, ValidationError


class LoginForm(FlaskForm):
    email = StringField(
        "email",
        validators=[
            InputRequired(),
            Email("Invalid email address!"),
        ],
    )
    password = PasswordField("password", validators=[InputRequired()])


def _valid_MFA_code(form, field):
    if str(field.data).isdigit():
        pass
        if 100000 <= int(field.data) <= 999999:
            return
    raise ValidationError(f"{field.data} is invalid MFA code")


class MFAForm(FlaskForm):
    mfa_code = StringField(
        "MFA Code",
        validators=[InputRequired(), _valid_MFA_code],
    )
