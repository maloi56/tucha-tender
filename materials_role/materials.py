from flask import Blueprint
from flask_login import login_required, current_user

import materials_role.materials_controller as controller

materials = Blueprint('materials', __name__, template_folder='templates', static_folder='static')


@materials.route('/')
@login_required
@controller.role_required
def index():
    return controller.index()


@materials.route('/selected')
@login_required
@controller.role_required
def selected():
    return controller.selected()


@materials.route('/tender/<id>')
@login_required
@controller.role_required
def tender(id):
    return controller.tender(id)


@materials.route("/rate_tender", methods=["POST"])
@login_required
@controller.role_required
def rate_tender():
    return controller.rate_tender()


@materials.route('/download_department_doc', methods=['POST'])
@login_required
@controller.role_required
def download_department_doc():
    return controller.download_department_doc()
