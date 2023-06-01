from functools import wraps
from flask import Blueprint, request, abort
from flask_login import login_required, current_user

import director_role.director_controller as controller

director = Blueprint('director', __name__, template_folder='templates', static_folder='static')


@director.route('/')
@login_required
@controller.role_required
def index():
    return controller.index()


@director.route('/selected')
@login_required
@controller.role_required
def selected():
    return controller.selected()


@director.route("/set_status", methods=["POST"])
@controller.role_required
def set_status():
    return controller.set_status()


@director.route('/download_docs', methods=['POST'])
@controller.role_required
def download_docs():
    return controller.download_docs()


@director.route('/tender/<id>')
@controller.role_required
@login_required
def tender(id):
    return controller.tender(id)
