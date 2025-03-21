from flask import Blueprint, render_template

statues_bp = Blueprint("statues_bp", __name__, url_prefix="")


@statues_bp.route("/")
def home_page():
    return render_template("home/index.html")


def page_not_found(e):
    return (
        render_template(
            "base.html", body="404 - Page Not Found", title="404 - Page Not Found"
        ),
        404,
    )


def invalid_method():
    error = "405: Method Not Allowed"
    return render_template("base.html", body=error)
