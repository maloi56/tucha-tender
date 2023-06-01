from flask import Blueprint
from flask_login import login_required, current_user

import hr_role.hr_controller as controller

hr = Blueprint('hr', __name__, template_folder='templates', static_folder='static')

@hr.route('/')
@login_required
@controller.role_required
def index():
    return controller.index()


@hr.route('/selected')
@login_required
@controller.role_required
def selected():
    return controller.selected()


@hr.route('/tender/<id>')
@login_required
@controller.role_required
def tender(id):
    return controller.tender(id)


@hr.route("/rate_tender", methods=["POST"])
@login_required
@controller.role_required
def rate_tender():
    return controller.rate_tender()


@hr.route('/download_department_doc', methods=['POST'])
@login_required
@controller.role_required
def download_department_doc():
    return controller.download_department_doc()
