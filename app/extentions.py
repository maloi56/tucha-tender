from flask import redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

from app.util.UserLogin import UserLogin

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

migrate = Migrate()

bootstrap = Bootstrap()


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('auth.login'))


