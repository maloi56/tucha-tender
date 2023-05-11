from bs4 import BeautifulSoup
from flask import Blueprint
from flask_login import login_required, current_user

import director_role.director_controller as director_controller
director = Blueprint('director', __name__, template_folder='templates', static_folder='static')


@director.before_request
def before_request():
    director_controller.before_request()


@director.teardown_request
def close_db(request):
    director_controller.close_db(request)


@director.route('/')
@login_required
def index():
    return director_controller.index()


@director.route('/other_selected')
@login_required
def other_selected():
    return director_controller.other_selected()


@director.route("/set_status", methods=["POST"])
def set_status():
    return director_controller.set_status()


@director.route('/downloadDocs', methods=['POST'])
def downloadDocs():
    return director_controller.downloadDocs()


@director.route('/tender/<id>')
@login_required
def tender(id):
    return director_controller.tender(id)
