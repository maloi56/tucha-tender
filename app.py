import locale
import time

from flask import Flask, redirect, g, url_for
from flask_login import LoginManager
from jinja2 import Environment
from jinja2.ext import do

from UserLogin import UserLogin
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from auth.login import auth
from director_role.director import director
from hr_role.hr import hr
from instruments_role.instruments import instruments
from materials_role.materials import materials
from tender_role.tender import tender
from tender_role.parser import scheduler, start_scheduler
from model import db


env = Environment(extensions=[do])


# load_dotenv()

def float_to_currency(value):
    locale.setlocale(locale.LC_ALL, '')  # Устанавливаем локаль по умолчанию
    return locale.currency(value, grouping=True, symbol=True)


def register_filters(app):
    app.jinja_env.filters['float_to_currency'] = float_to_currency


# FLASK
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = '7e05aef5e3609333d0ac992767e26bfcf88cdd87'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:MASTERKEY@localhost/tender'

app.register_blueprint(director, url_prefix='/director')
app.register_blueprint(hr, url_prefix='/hr')
app.register_blueprint(instruments, url_prefix='/instruments')
app.register_blueprint(materials, url_prefix='/materials')
app.register_blueprint(tender, url_prefix='/tender')
app.register_blueprint(auth, url_prefix='/auth')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

db.init_app(app)
migrate = Migrate(app,  db)

scheduler.init_app(app)
# FLASK


with app.app_context():
    time.sleep(0.5)
    db.create_all()
    # dbase.init_admin()
    register_filters(app)  # зарегистрировать фильтры


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('auth.login'))


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('auth.login'))


if __name__ == "__main__":
    start_scheduler()
    app.run(debug=True, use_reloader=True)
