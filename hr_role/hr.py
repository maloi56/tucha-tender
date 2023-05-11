from bs4 import BeautifulSoup
from flask import Blueprint
from flask_login import login_required, current_user

import hr_role.hr_controller as hr_controller
hr = Blueprint('hr', __name__, template_folder='templates', static_folder='static')


@hr.before_request
def before_request():
    hr_controller.before_request()


@hr.teardown_request
def close_db(request):
    hr_controller.close_db(request)


@hr.route('/')
@login_required
def index():
    return hr_controller.index()


@hr.route('/other_selected')
@login_required
def other_selected():
    return hr_controller.other_selected()


@hr.route('/tender/<id>')
@login_required
def tender(id):
    return hr_controller.tender(id)


@hr.route("/rate_tender", methods=["POST"])
def rate_tender():
    return hr_controller.rate_tender()


@hr.route('/download_department_doc', methods=['POST'])
@login_required
def download_department_doc():
    return hr_controller.download_department_doc()
