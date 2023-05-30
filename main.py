import locale
import sqlite3
import time
import asyncio

import pymorphy3
from flask import Flask, redirect, g, url_for
from flask_login import LoginManager
from flask_mail import Mail, Message
from jinja2 import Environment
from jinja2.ext import do

from FDataBase import FDataBase
from UserLogin import UserLogin
from auth.login import auth
from director_role.director import director
from hr_role.hr import hr
from instruments_role.instruments import instruments
from materials_role.materials import materials
from tender_role.tender import tender
from tender_role.parser import start_scheduler

env = Environment(extensions=[do])


# load_dotenv()

def float_to_currency(value):
    locale.setlocale(locale.LC_ALL, '')  # Устанавливаем локаль по умолчанию
    return locale.currency(value, grouping=True, symbol=True)


def register_filters(app):
    app.jinja_env.filters['float_to_currency'] = float_to_currency


morph = pymorphy3.MorphAnalyzer()
data = {}
res = {}
date = ""
priceFrom = 0
priceTo = 0
global_count = 0

# FLASK
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = '7e05aef5e3609333d0ac992767e26bfcf88cdd87'

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



# FLASK

baseStopWords = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                 "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", "ст"]

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

DATABASE = 'database.db'
global_count = 0

dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_database()
    dbase = FDataBase(db)


def get_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


def get_database():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = get_db()
    return g.link_db

with app.app_context():
    time.sleep(0.5)
    # find_tenders(start_time = time.time())
    register_filters(app)  # зарегистрировать фильтры


@login_manager.user_loader
def load_user(user_id):
    db = get_database()
    dbasee = FDataBase(db)
    return UserLogin().fromDB(user_id, dbasee)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('auth.login'))


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    start_scheduler()
    app.run(debug=True, use_reloader=False)
