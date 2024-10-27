import logging

from flask import Blueprint, render_template, request, redirect, url_for, session

from backend.server.models.Client import custom_sso_login, MFA_auth, Client
from backend.server.models.forms import LoginForm, MFAForm

login_bp = Blueprint("login_bp", __name__, url_prefix="")
logger = logging.getLogger(__name__)
client = Client()


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # TODO: run using HTTPS
    login_form = LoginForm()

    if request.method == "GET":
        return render_template("login.html", form=login_form)

    if login_form.validate_on_submit():
        try:
            session["csrf_garmin"] = custom_sso_login(
                login_form.email.data, login_form.password.data, client=client
            )
        except Exception as e:
            print(e)
        # TODO: validate successful login for client
        redirect(url_for(".get_mfa_code"))

    else:
        logger.debug(f"{login_form.errors}")

    return render_template("login.html", form=login_form)


@login_bp.route("/mfa_code", methods=["GET", "POST"])
def get_mfa_code():
    mfa_form = MFAForm()

    if request.method == "GET":
        return render_template("mfa_code.html", form=mfa_form)

    if mfa_form.validate_on_submit():
        mfa_code = mfa_form.mfa_code.data
        try:
            MFA_auth(session["csrf_garmin"], client, mfa_code)
        except Exception as e:
            print(e)
        # TODO: validate correct MFA code
        # TODO: redirect to success
        redirect(url_for("hello"))
    else:
        logger.debug(f"{mfa_form.errors}")

    return render_template("mfa_code.html", form=mfa_form)
