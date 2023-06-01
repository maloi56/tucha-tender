from flask import Blueprint
from flask_login import login_required, current_user

import instruments_role.instruments_controller as controller

instruments = Blueprint('instruments', __name__, template_folder='templates', static_folder='static')


@instruments.route('/')
@login_required
@controller.role_required
def index():
    return controller.index()


@instruments.route('/selected')
@login_required
@controller.role_required
def selected():
    return controller.selected()


@instruments.route('/tender/<id>')
@login_required
@controller.role_required
def tender(id):
    return controller.tender(id)


@instruments.route("/rate_tender", methods=["POST"])
@login_required
@controller.role_required
def rate_tender():
    return controller.rate_tender()


@instruments.route('/download_department_doc', methods=['POST'])
@login_required
@controller.role_required
def download_department_doc():
    return controller.download_department_doc()
