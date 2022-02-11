from flask import Blueprint, render_template
from flask_login import login_required

pages_blueprint = Blueprint("pages_blueprint", __name__, url_prefix="/pages")


@pages_blueprint.route("/profile/<string:login>", methods=["GET"])
@login_required
def cabinet(login):
    return render_template("personal-cabinet.html", name=login)
