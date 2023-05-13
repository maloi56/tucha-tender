from flask import Blueprint
from flask_login import login_required

import tender_role.tender_controller as controller

tender = Blueprint('tender', __name__, template_folder='templates', static_folder='static')


@tender.before_request
def before_request():
    controller.before_request()


@tender.teardown_request
def close_db(request):
    controller.close_db(request)


@tender.route('/')
@login_required
@controller.role_required
def index():
    return controller.index()


@tender.route('/considered')
@login_required
@controller.role_required
def considered():
    return controller.considered()


@tender.route('/selected')
@login_required
@controller.role_required
def selected():
    return controller.selected()


@tender.route('/select', methods=['POST'])
@login_required
@controller.role_required
def select():
    return controller.select()


@tender.route('/delete', methods=['POST'])
@login_required
@controller.role_required
def delete():
    return controller.delete()


@tender.route('/rules', methods=['GET', 'POST'])
@login_required
@controller.role_required
def rules():
    return controller.rules()


@tender.route('/add_rule', methods=['POST'])
@login_required
@controller.role_required
def add_rule():
    return controller.add_rule()


@tender.route('/add_optional_rules', methods=['POST'])
@login_required
@controller.role_required
def add_optional_rules():
    return controller.add_optional_rules()


# Страница для удаления слова из правил
@tender.route('/remove_word', methods=['POST'])
@login_required
@controller.role_required
def remove_word():
    return controller.remove_word()


@tender.route('/add_ban_rule', methods=['POST'])
@login_required
@controller.role_required
def add_ban_rule():
    return controller.add_ban_rule()


@tender.route('/find_tenders', methods=['POST'])
@login_required
def find_tenders():
    return controller.find_tenders()


# Страница для удаления слова из правил
@tender.route('/remove_ban_word', methods=['POST'])
@login_required
@controller.role_required
def remove_ban_word():
    return controller.remove_ban_word()


@tender.route('/tender/<id>')
@login_required
@controller.role_required
def tender_id(id):
    return controller.tender_id(id)


@tender.route('/upload_doc', methods=['POST'])
@login_required
@controller.role_required
def upload_doc():
    return controller.upload_doc()
