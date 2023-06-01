from flask import Blueprint, abort
from flask_login import login_required, current_user
import auth.login_controller as controller

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@auth.route("/register", methods=["POST", "GET"])
@login_required
def register():
    print(current_user.get_role())
    if current_user.get_role() != "admin":
        return abort(403)
    return controller.register()


@auth.route("/login", methods=["POST", "GET"])
def login():
    return controller.login()


@auth.route("/logout")
@login_required
def logout():
    return controller.logout()
