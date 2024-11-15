from flask import Blueprint, render_template

statues_bp = Blueprint("statues_bp", __name__, url_prefix="")


@statues_bp.route("/")
def hello():
    return render_template("base.html", body="Hello, world!")


def page_not_found(e):
    return render_template("not_found.html", msg="404 - Page Not Found"), 404
