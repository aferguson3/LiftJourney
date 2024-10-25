from flask import Blueprint, render_template, request

from backend.server.models.forms.LoginForm import LoginForm

login_bp = Blueprint("login_bp", __name__, url_prefix="")


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # TODO: run using HTTPS
    login_form = LoginForm()

    if request.method == "POST":
        if login_form.validate_on_submit():
            print("validated")
            pass
            # if not pathlib.Path.exists(CREDS_PATH):
            #     pathlib.Path.mkdir(CREDS_PATH)
            # config = dotenv_values(str(ENV_PATH))
            # # garth.login(config["EMAIL"], config["PASSWORD"], mfa_prompt="")
            # garth.save(str(CREDS_PATH)
        else:
            print("invalid")

    return render_template("login.html", form=login_form)


@login_bp.route("/mfa_code", methods=["GET", "POST"])
def get_mfa_code():
    return render_template("base.html")
