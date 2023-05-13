import requests
from bs4 import BeautifulSoup
import pymorphy3
from fuzzywuzzy import fuzz
import time
import re
from flask import Flask, session, render_template, request, url_for, current_app, redirect, flash, send_file, g, \
    url_for, abort, make_response, blueprints
import sqlite3
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2.ext import do
import locale
from datetime import datetime
import tempfile
import os
import shutil
import mimetypes
import magic
import asyncio
import aiohttp
import math
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from FDataBase import FDataBase
from flask_principal import Identity, Principal, Permission, RoleNeed, identity_loaded, identity_changed, \
    AnonymousIdentity
from dotenv import load_dotenv
from forms import LoginForm, RegisterForm, AddFilterForm, DeleteFilterForm, AddBanForm, DeleteBanForm, \
    AddOptionalRulesForm
from io import BytesIO

from director_role.director import director
from hr_role.hr import hr
from instruments_role.instruments import instruments
from materials_role.materials import materials
from tender_role.tender import tender

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

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

principal = Principal(app)

# Определение ролей
hr_role = RoleNeed('hr')
tender_role = RoleNeed('tender')
instruments_role = RoleNeed('instruments')
materials_role = RoleNeed('materials')
director_role = RoleNeed('director')

# Создание объекта Permission на основе ролей
hr_permission = Permission(hr_role)
tender_permission = Permission(tender_role)
instruments_permission = Permission(instruments_role)
materials_permission = Permission(materials_role)
director_permission = Permission(director_role)

department_permission = Permission(hr_role, director_role, instruments_role, materials_role)

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


async def get_page_data(session, page, stopWords, filter, priceFrom, priceTo, formatted_date):
    global global_count
    url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber={page}&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&ppRf615=on&af=on&priceFromGeneral={priceFrom}&priceToGeneral={priceTo}&currencyIdGeneral=-1&applSubmissionCloseDateTo={formatted_date}&customerPlace=5277327%2C5277335&customerPlaceCodes=50000000000%2C77000000000&OrderPlacementSmallBusinessSubject=on&OrderPlacementRnpData=on&OrderPlacementExecutionRequirement=on&orderPlacement94_0=0&orderPlacement94_1=0&orderPlacement94_2=0"
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "lxml")
        container = soup.find("div", class_="col-9")
        if container is not None:
            card_items = container.find_all("div", {"class": "registry-entry__form"})
        else:
            card_items = []
        for ci in card_items:
            flag = False
            card_data = ci.find_all("div", {"class": "registry-entry__body-value"})
            right_block = ci.find_all("div", {"class": "registry-entry__right-block"})
            if len(right_block) != 0:
                price = right_block[0].find("div", {"class": "price-block__value"})
                block = ci.find("div", {"class": "data-block__title"}, text="Окончание подачи заявок")
                if block:
                    date_value = block.find_next_sibling("div", {"class": "data-block__value"}).text
                else:
                    print("No date found")
                price_value = 0 if price is None else int(re.sub(r'\D', '', price.text.strip())) / 100
            href = ci.find_all("a")
            if len(card_data) != 0:
                text = card_data[0].text.lower()
                t = re.sub(r"[^\w\s]", "", text)
                words = t.split()
                normalized_text = " ".join([morph.parse(word)[0].normal_form for word in words]).split()
                for word in stopWords:
                    if word in normalized_text:
                        flag = True
                        break
                if flag == False:
                    id = str(re.sub(r'\D', '', href[2].text))
                    flag_1 = False
                    text_1 = re.sub(r"[^\w\s]", "", card_data[0].text)
                    baseFiltered = [word for word in text_1.split() if word not in baseStopWords]
                    for word in baseFiltered:
                        for fil_word in filter:
                            a = fuzz.partial_ratio(fil_word, word)
                            if a == 100:
                                if datetime.strptime(date_value, '%d.%m.%Y') >= datetime.today():
                                    res[str(id)] = {
                                        "id": id,
                                        "title": card_data[0].text,
                                        "price": price_value,
                                        "date": date_value,
                                        "href": href[2].get("href")
                                    }
                                    print(fil_word + " " + word)
                                    print(res[id])
                                    flag_1 = True
                                    break
                        if flag_1:
                            break
                else:
                    print("В бан - " + card_data[0].text)
    print(f"[INFO] Обработал страницу {page}")
    global_count += 1
    print(global_count)


async def gather_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        # conn = get_db()
        # cur = conn.cursor()
        # dbase.init_db(cur)
        optRules = dbase.get_optional_rules()
        if len(optRules) != 0:
            date = optRules[0]['date']
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')
            priceFrom = optRules[0]['priceFrom']
            priceTo = optRules[0]['priceTo']
        else:
            formatted_date = str(datetime.today().strftime("%d-%m-%Y"))
            priceFrom = 0
            priceTo = 100000
        filter = get_filter_words()
        stopWords = get_ban_words()
        for page in range(1, 10):
            task = asyncio.create_task(
                get_page_data(session, page, stopWords, filter, priceFrom, priceTo, formatted_date))
            tasks.append(task)

        await asyncio.gather(*tasks)


def get_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


def get_database():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = get_db()
    return g.link_db


@app.route('/find_tenders', methods=['POST'])
@login_required
def find_tenders():
    asyncio.run(gather_data())
    dbase.insert_tenders(res)
    selected_items = dbase.get_considered('отбор')
    return render_template('considered.html', title='Рассматриваемые заявки', selected_items=selected_items,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


@app.route('/')
@login_required
def index():
    # dbase.init_db()
    return render_template('index.html', title="Интеллектуальная поддержка отбора заявок на сайте закупок",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


@app.route('/considered')
@login_required
@tender_permission.require(http_exception=403)
def considered():
    selected_items = dbase.get_considered('отбор')
    return render_template('considered.html', title='Рассматриваемые заявки', selected_items=selected_items,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


@app.route('/selected')
@login_required
def selected():
    selected_items = dbase.get_selected('отбор')
    return render_template('selected.html', selected_items=selected_items,
                           title="Выбранные заявки",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


@app.route('/other_selected')
@login_required
@department_permission.require(http_exception=403)
def other_selected():
    selected_items = dbase.get_selected('отбор')
    return render_template('other_selected.html', selected_items=selected_items, title="Выбранные заявки",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def get_reasonability(rate):
    if rate >= 1:
        return "участие небходимо"
    elif rate >= 0.8:
        return "участие целесообразно"
    elif rate >= 0.7:
        return "участие рисковано"
    else:
        return "участие нецелесообразно"


def get_self_price(hr, instruments, materials):
    try:
        return hr['costprice'] + instruments['costprice'] + materials['costprice']
    except Exception as err:
        print(err)


def get_sppr_info(self_price, hr, instruments, materials, tender):
    try:
        if (self_price != 0 and hr['rate'] != 0 and instruments['rate'] != 0 and materials['rate'] != 0):
            average_rate = (hr['rate'] + instruments['rate'] + materials['rate']) / 3
            reasonability = int((average_rate / 10) * (tender['price'] / (self_price + 1)) * 100)
            support_decision = get_reasonability(reasonability)
            return average_rate, str(reasonability) + '%', support_decision
        else:
            return 'Не все отделы выставили оценки!', 'Не все отделы выставили оценки!', 'Не все отделы выставили оценки!'
    except:
        return 0, 0, 0


@app.route('/tender/<role>/<id>')
@login_required
def tender(role, id):
    tender = dbase.get_tender(id)
    roles = dbase.get_roles()
    dic = []
    for row in roles:
        dic.append(row['name'])
    if not tender or role not in dic or role != current_user.get_role():
        abort(404)
    rate_info = []
    hr_info = dbase.get_tender_rate(id, 'hr')
    instruments_info = dbase.get_tender_rate(id, 'instruments')
    materials_info = dbase.get_tender_rate(id, 'materials')
    self_price = 1
    average_rate = 1
    reasonability = 0
    support_decision = ""
    if current_user.get_role() == 'director':
        self_price = get_self_price(hr_info, instruments_info, materials_info)
        average_rate, reasonability, support_decision = get_sppr_info(self_price, hr_info, instruments_info,
                                                                      materials_info, tender)
    else:
        rate_info = dbase.get_tender_rate(id, role)
    return render_template('tender.html', tender=tender,
                           self_price=self_price,
                           support_decision=support_decision,
                           reasonability=reasonability,
                           average_rate=average_rate,
                           rate_info=rate_info,
                           hr_info=hr_info,
                           instruments_info=instruments_info,
                           materials_info=materials_info,
                           title=f"Тендерная заявка номер: {id}",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


# @app.route('/select', methods=['POST'])
# @login_required
# def select():
#     item_id = request.form['id']
#     dbase.select_tender(item_id)
#     return redirect(url_for('considered'))


@app.route('/downloadDocs', methods=['POST'])
def downloadDocs():
    # Передавать список доступных документов и мб загрузку по одному отдельному
    blocks = {}
    type = ""
    id = request.form['id'].split('=')[-1]
    print(id)
    if id[0] == "0" and len(id) > 11:
        url = f"https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber={id}"
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        blocks = soup.find("div", class_="blockFilesTabDocs").find_all("span", {"class": "section__value"})
        type = "44"
    else:
        url = f"https://zakupki.gov.ru/epz/order/notice/notice223/documents.html?noticeInfoId={id}"
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        pre_blocks = soup.find_all("div", class_="attachment__value")
        blocks = pre_blocks[3].find_all("span", class_="count")
        type = "223"
        # print(blocks[1].find_all("span", {"class": "count "}))

    # создаем временную папку для сохранения файлов
    tempdir = tempfile.mkdtemp()

    # скачиваем файлы и сохраняем их в временной папке
    for block in blocks:
        href = block.find_all("a")
        url = href[0].get("href") if type == "44" else "https://zakupki.gov.ru" + href[1].get("href")
        print(url)
        text = href[0].text if type == "44" else href[1].text
        clean_text = re.sub(r'[^\w\s]', '', text).strip()

        mime = magic.Magic(mime=True)

        r = requests.get(url, headers=headers)
        content_type = mime.from_buffer(r.content)
        ext = mimetypes.guess_extension(content_type)
        f_name = clean_text + ext if ext else clean_text + ".pdf"
        filename = os.path.join(tempdir, f_name)
        with open(filename, 'wb') as f:
            f.write(r.content)

    # создаем zip-архив с содержимым временной папки
    zip_filename = f'Заявка - {id}.zip'
    shutil.make_archive(zip_filename[:-4], 'zip', tempdir)

    # отправляем zip-архив клиенту в качестве ответа на запрос
    return send_file(zip_filename, as_attachment=True)


# Функция для получения списка слов из правил
def get_filter_words():
    # Здесь должен быть код для получения списка слов из правил
    # Предположим, что мы просто разбиваем правила на слова
    rules = dbase.get_filter_words()
    words = []
    for rule in rules:
        words += rule['word'].split()
    return set(words)


# Функция для получения списка слов из правил
def get_ban_words():
    rules = dbase.get_ban_words()
    words = []
    for rule in rules:
        words += rule['word'].split()
    return set(words)


@app.route('/add_rule', methods=['POST'])
def add_rule():
    if request.method == "POST":
        new_rule = request.form['rule']
        if dbase.add_rule(new_rule):
            flash('Новое правило было успешно добавлено!')
        else:
            flash('Ошибка при добавлении правила')
        return redirect(url_for('rules'))


@app.route('/add_optional_rules', methods=['POST'])
def add_optional_rules():
    priceFrom = int(request.form['optional_rule_priceFrom'])
    priceTo = int(request.form['optional_rule_priceTo'])
    date = request.form['optional_rule_date']
    if dbase.add_optional_rule(priceFrom, priceTo, date):
        flash('Новое правило было успешно добавлено!')
    else:
        flash('Ошибка при добавлении правила')
    return redirect(url_for('rules'))


# Страница для удаления слова из правил
@app.route('/remove_word', methods=['POST'])
def remove_word():
    word = request.form['word']
    if dbase.delete_filter_word(word):
        flash('Слово "{}" было успешно удалено из правил!'.format(word))
    else:
        flash('Ошибка при удалении слова')
    return redirect(url_for('rules'))


@app.route('/add_ban_rule', methods=['POST'])
def add_ban_rule():
    new_rule = request.form['ban_rule']
    if dbase.add_ban_rule(new_rule):
        flash('Новое правило было успешно добавлено!')
    else:
        flash('Ошибка при добавлении правила!')
    return redirect(url_for('rules'))


# Страница для удаления слова из правил
@app.route('/remove_ban_word', methods=['POST'])
def remove_ban_word():
    word = request.form['ban_rule']
    if dbase.delete_ban_word(word):
        flash('Слово "{}" было успешно удалено из правил!'.format(word))
    else:
        flash('Ошибка при удалении слова')
    return redirect(url_for('rules'))


# Страница "База правил"
@app.route('/rules', methods=['GET', 'POST'])
@login_required
@tender_permission.require(http_exception=403)
def rules():
    rules = get_filter_words()
    ban_rules = get_ban_words()
    optional_rules = dbase.get_optional_rules()

    add_rule_form = AddFilterForm()
    delete_rule_form = DeleteFilterForm()
    delete_rule_form.word.choices = [(word, word) for word in rules]

    add_ban_form = AddBanForm()
    delete_ban_form = DeleteBanForm()
    delete_ban_form.ban_rule.choices = [(word, word) for word in ban_rules]
    add_optional_rules_form = AddOptionalRulesForm()

    return render_template('rules.html', title="База правил",
                           menu=current_user.get_menu() if current_user.is_authenticated else [],
                           rules=rules, add_rule_form=add_rule_form, delete_rule_form=delete_rule_form,
                           ban_rules=ban_rules, add_ban_form=add_ban_form, delete_ban_form=delete_ban_form,
                           optional_rules=optional_rules, add_optional_rules_form=add_optional_rules_form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(f'/{current_user.get_role()}/')
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByLogin(form.login.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            identity_changed.send(current_app._get_current_object(), identity=Identity(user['id']))
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(f"/{dbase.get_role(user['role'])}/")

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", title="Авторизация", form=form,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for("login"))


# def addUser(role, login, hpsw):
#     try:
#         conn = get_db()
#         cur = conn.cursor()
#         cur.execute(f"SELECT COUNT() as `count` FROM users WHERE login LIKE '{login}'")
#         res = cur.fetchone()
#         if res['count'] > 0:
#             print("Пользователь с таким login уже существует")
#             return False
#
#         tm = math.floor(time.time())
#         cur.execute("SELECT id from roles WHERE name = ?", (role,))
#         role_id = cur.fetchone()
#         print(role_id['id'])
#         cur.execute("INSERT INTO users (role, login, psw, time) VALUES(?, ?, ?, ?)", (role_id['id'], login, hpsw, tm))
#         conn.commit()
#         conn.close()
#     except sqlite3.Error as e:
#         print("Ошибка добавления пользователя в БД " + str(e))
#         return False
#
#     return True


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form['psw'])
        res = dbase.addUser(form.role.data, form.login.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", title="Регистрация", form=form,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


# @app.route("/set_status", methods=["POST", "GET"])
# def set_status():
#     if request.method == "POST":
#         dbase.set_status(request.form['tender_id'], request.form['status'])
#     return redirect(url_for('other_selected'))


@app.route("/rate_tender", methods=["POST", "GET"])
def rate_tender():
    if request.method == "POST":
        role = current_user.get_role()
        session.pop('_flashes', None)
        if request.form['rating'] \
                and len(request.form['costprice']) > 2:
            res = dbase.rate_tender(role, request.form['tender_id'], request.form['costprice'], request.form['comment'],
                                    request.form['rating'])
            print(res)
            if res:
                flash("Оценка отправлена", "success")
                return redirect(url_for('other_selected'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
    tender = dbase.get_tender(request.form['tender_id'])
    if not tender:
        abort(404)
    rate_info = dbase.get_tender_rate(request.form['tender_id'], role)
    return render_template("tender.html", title=f"Тендерная заявка номер: {request.form['tender_id']}",
                           rate_info=rate_info, tender=tender,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


@app.route('/upload_doc', methods=['POST', 'GET'])
def upload_doc():
    if request.method == 'POST':
        file = request.files['file'].read()
        role = request.form['role']
        tender_id = request.form['tender_id']
        if len(file) > 0:
            try:
                res = dbase.upload_doc(file, role, tender_id)
                if not res:
                    flash("Ошибка обновления аватара", "error")
                    return redirect(f'/tender/tender/{tender_id}')
                flash("Файл загружен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
            return redirect(f'/tender/tender/{tender_id}')
        else:
            flash("Ошибка чтения файла", "error")
            return redirect(f'/tender/tender/{tender_id}')


@app.route('/download_department_doc', methods=['POST', 'GET'])
@login_required
def download_department_doc():
    if request.method == 'POST':
        role = current_user.get_role()
        tender_id = request.form['tender_id']
        doc = dbase.get_department_doc(tender_id, role)['document']
        if doc is not None:
            mime = magic.Magic(mime=True)
            content_type = mime.from_buffer(doc)
            ext = mimetypes.guess_extension(content_type)
            clean_text = role + "-" + tender_id
            f_name = clean_text + ext if ext else clean_text + ".pdf"
            return send_file(BytesIO(doc), download_name=f_name, as_attachment=True)
        else:
            flash("Не найдено документов", "error")
            return redirect(f'/tender/{role}/{tender_id}')


with app.app_context():
    time.sleep(0.5)
    # find_tenders(start_time = time.time())
    register_filters(app)  # зарегистрировать фильтры


@login_manager.user_loader
def load_user(user_id):
    db = get_database()
    dbasee = FDataBase(db)
    return UserLogin().fromDB(user_id, dbasee)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    try:
        user_role = identity.user.get_role()
        # Добавление роли пользователя в идентификацию
        if user_role == 'hr':
            identity.provides.add(hr_role)
        elif user_role == 'tender':
            identity.provides.add(tender_role)
        elif user_role == 'instruments':
            identity.provides.add(instruments_role)
        elif user_role == 'materials':
            identity.provides.add(materials_role)
        elif user_role == 'director':
            identity.provides.add(director_role)
    except:
        print("asd")


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
