import logging

import garth
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from werkzeug import Response

from backend.server.authenticate import custom_sso_login, mfa_authentication, Client
from backend.server.models.forms import LoginForm, MFAForm
from backend.server.routes.status_codes import invalid_method
from backend.src.garmin_interaction import load_oauth_tokens, is_oauth_tokens_active

login_bp = Blueprint("login_bp", __name__, url_prefix="")
logger = logging.getLogger(__name__)
client = Client()


def login_check() -> Response | None:
    caller = request.path
    if is_oauth_tokens_active():
        return None
    if not load_oauth_tokens():
        session["caller"] = caller
        return redirect(url_for(".login"))


def _validate_login(
    email: str, password: str, cur_client: garth.Client = client
) -> (Response | None, None | str):
    csrf_garmin = custom_sso_login(email, password, client=cur_client)
    error = None

    if csrf_garmin is not None:
        logger.info(f"Successful SSO login for {email}.")
        session["csrf_garmin"] = csrf_garmin
        return redirect(url_for(".mfa_handler")), None
    else:
        error = f"Unsuccessful SSO login for {email}"
        logger.info(error)
        return None, error


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    match request.method:
        case "GET":
            return login_get()
        case "POST":
            return login_process()
        case _:
            return invalid_method()


def login_get():
    login_form = LoginForm()
    if load_oauth_tokens():
        return redirect("/", 302)

    return render_template("login/login.html", form=login_form)


def login_process() -> (Response | int | None, None | str):
    # TODO: run using HTTPS
    login_form = LoginForm()
    oauth_tokens_exist = load_oauth_tokens()
    error = None

    if oauth_tokens_exist is True:
        return 200, error

    elif not login_form.validate_on_submit():
        logger.debug(f"Errors: {login_form.errors}")
        error = login_form.errors

    elif oauth_tokens_exist is False:
        email = login_form.email.data
        password = login_form.password.data
        resp, error = _validate_login(email, password)
        if error is None:
            return resp, error

    return render_template("login/login.html", form=login_form, error=error), error


def _validate_mfa_code(mfa_code: str, cur_client: garth.Client = client) -> str | None:
    error = mfa_authentication(session["csrf_garmin"], cur_client, mfa_code)

    if error is not None:
        logger.info(error)
        return f"Invalid code. Enter the 6 digit MFA Code."


@login_bp.route("/login/mfa_code", methods=["GET", "POST"])
def mfa_handler():
    match request.method:
        case "GET":
            mfa_form = MFAForm()
            return render_template("login/mfa_code.html", form=mfa_form)
        case "POST":
            return get_mfa_code()
        case _:
            return invalid_method()


def get_mfa_code() -> (Response, str):
    mfa_form = MFAForm()
    error = None
    if not mfa_form.validate_on_submit():
        error = mfa_form.errors
        logger.debug(f"{error}")
    else:
        error = _validate_mfa_code(mfa_form.mfa_code.data, client)
        if error is None:
            caller = session.get("caller")
            caller = "/" if caller is None else caller
            return redirect(caller, 302)

    return render_template("login/mfa_code.html", form=mfa_form, error=error)
