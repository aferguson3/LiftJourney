import logging

import garth
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    Response,
)

from backend.server.authenticate import custom_sso_login, mfa_authentication, Client
from backend.server.models.forms import LoginForm, MFAForm
from backend.src.garmin_interaction import load_oauth_tokens, is_oauth_tokens_active

login_bp = Blueprint("login_bp", __name__, url_prefix="")
logger = logging.getLogger(__name__)
client = Client()


def login_check():
    if not is_oauth_tokens_active():
        return render_template("base.html", body="401: Unauthorized"), 401


def _validate_login(
    email: str, password: str, cur_client: garth.Client = client
) -> Response | None:
    csrf_garmin = custom_sso_login(email, password, client=cur_client)
    if csrf_garmin is not None:
        logger.info(f"Successful SSO login for {email}.")
        session["csrf_garmin"] = csrf_garmin
        return redirect(url_for(".get_mfa_code"))
    else:
        logger.info(f"Unsuccessful SSO login for {email}")


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # TODO: run using HTTPS
    login_form = LoginForm()
    oauth_tokens_exist = load_oauth_tokens()

    if oauth_tokens_exist is True:
        return render_template("base.html", body="Success", title="Login Success")

    if not login_form.validate_on_submit():
        if request.method == "POST":
            logger.debug(f"Errors: {login_form.form_errors}")
        return render_template("login/login.html", form=login_form)

    if oauth_tokens_exist is False:
        email = login_form.email.data
        password = login_form.password.data

        _resp_or_none = _validate_login(email, password)
        if _resp_or_none is not None:
            return _resp_or_none

    return render_template("login/login.html", form=login_form)


def _validate_mfa_code(mfa_code: str, cur_client: garth.Client = client) -> str | None:
    error = mfa_authentication(session["csrf_garmin"], cur_client, mfa_code)

    if error is None:
        return render_template("base.html", body="Success", title="MFA Code")
    else:
        logger.info(error)


@login_bp.route("/mfa_code", methods=["GET", "POST"])
def get_mfa_code():
    mfa_form = MFAForm()

    if request.method == "GET" or not mfa_form.validate_on_submit():
        if request.method == "POST":
            logger.debug(f"{mfa_form.errors}")
        return render_template("login/mfa_code.html", form=mfa_form)

    _resp_or_none = _validate_mfa_code(mfa_form.mfa_code.data, client)
    if _resp_or_none is not None:
        return _resp_or_none, 302
