from functools import wraps
from flask import Blueprint, request, abort
from flask_login import login_required, current_user

import director_role.director_controller as controller
director = Blueprint('director', __name__, template_folder='templates', static_folder='static')


@director.before_request
def before_request():
    controller.before_request()


@director.teardown_request
def close_db(request):
    controller.close_db(request)


@director.route('/')
@login_required
@controller.role_required
def index():
    return controller.index()


@director.route('/other_selected')
@login_required
@controller.role_required
def other_selected():
    return controller.other_selected()


@director.route("/set_status", methods=["POST"])
@controller.role_required
def set_status():
    return controller.set_status()


@director.route('/downloadDocs', methods=['POST'])
@controller.role_required
def downloadDocs():
    return controller.downloadDocs()


@director.route('/tender/<id>')
@controller.role_required
@login_required
def tender(id):
    return controller.tender(id)
