import logging

from flask import Blueprint, render_template, request, redirect, url_for, session

from backend.server.authenticate import custom_sso_login, mfa_authentication, Client
from backend.server.models.forms import LoginForm, MFAForm
from backend.src.garmin_interaction import load_garmin_client

login_bp = Blueprint("login_bp", __name__, url_prefix="")
logger = logging.getLogger(__name__)
client = Client()


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # TODO: run using HTTPS
    login_form = LoginForm()
    resume_status = load_garmin_client()

    if resume_status == 0:
        return render_template("base.html", body="Success", title="Login Success")

    if not login_form.validate_on_submit():
        if request.method == "POST":
            logger.debug(f"Errors: {login_form.form_errors}")
        return render_template("login.html", form=login_form)

    if resume_status > 0:
        csrf_garmin = custom_sso_login(
            login_form.email.data, login_form.password.data, client=client
        )

        if csrf_garmin is not None:
            logger.info(f"Successful SSO login for {login_form.email.data}.")
            session["csrf_garmin"] = csrf_garmin
            return redirect(url_for(".get_mfa_code"))
        else:
            logger.info(f"Unsuccessful SSO login for {login_form.email.data}")

    return render_template("login.html", form=login_form)


@login_bp.route("/mfa_code", methods=["GET", "POST"])
def get_mfa_code():
    mfa_form = MFAForm()

    if request.method == "GET" or not mfa_form.validate_on_submit:
        if request.method == "POST":
            logger.debug(f"{mfa_form.errors}")
        return render_template("mfa_code.html", form=mfa_form)

    _error = mfa_authentication(session["csrf_garmin"], client, mfa_form.mfa_code.data)
    if _error is None:
        return render_template("base.html", body="Success", title="MFA Code")
    else:
        return render_template("mfa_code.html", form=mfa_form)
