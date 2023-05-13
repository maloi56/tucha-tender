import mimetypes
import sqlite3
import magic
from functools import wraps
from io import BytesIO
from flask import render_template, url_for, redirect, flash, g, abort, send_file, request
from flask_login import current_user
from FDataBase import FDataBase
from instruments_role.forms import RateTenderForm, DownloadDocsForm

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

DATABASE = 'database.db'

def role_required(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if request.endpoint.split('.')[0] != current_user.get_role():
            abort(403)
        return route_func(*args, **kwargs)
    return wrapper


def check_role():
    return True if current_user.get_role() == 'instruments' else False


def get_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


def get_database():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = get_db()
    return g.link_db


dbase = None


def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_database()
    dbase = FDataBase(db)


def close_db(request):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


def selected():
    if check_role():
        print(current_user.get_menu())
        selected_items = dbase.get_selected('отбор')
        return render_template('instruments/selected.html', selected_items=selected_items, title="Выбранные заявки",
                               menu=current_user.get_menu() if current_user.is_authenticated else [])
    else:
        flash('Нет доступа')
        redirect(url_for("index"))


def index():
    # dbase.init_db()
    return render_template('instruments/index.html', title="Интеллектуальная поддержка отбора заявок на сайте закупок",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def tender(id):
    tender = dbase.get_tender(id)
    if not tender or not check_role():
        abort(404)
    rate_info = dbase.get_tender_rate(id, current_user.get_role())

    download_form = DownloadDocsForm()
    download_form.tender_id.data = id

    rate_form = RateTenderForm()
    rate_form.tender_id.data = id
    rate_form.costprice.data = rate_info['costprice']
    rate_form.slider.data = rate_info['rate']
    rate_form.comment.data = rate_info['comment']

    return render_template('instruments/tender.html',
                           tender=tender,
                           download_form=download_form,
                           rate_form=rate_form,
                           rate_info=rate_info,
                           title=f"Тендерная заявка номер: {id}",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def rate_tender():
    form = RateTenderForm()
    tender = dbase.get_tender(form.tender_id.data)
    if not tender:
        abort(404)
    role = current_user.get_role()
    if form.validate_on_submit():
        res = dbase.rate_tender(role, tender['id'], form.costprice.data, form.comment.data, form.slider.data)
        print(res)
        if res:
            flash("Оценка отправлена", "success")
            return redirect(url_for('.selected'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    rate_info = dbase.get_tender_rate(tender['id'], role)
    return render_template("instruments/tender.html", title=f"Тендерная заявка номер: {tender['id']}",
                           rate_info=rate_info, tender=tender,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def download_department_doc():
    form = DownloadDocsForm()
    if form.validate_on_submit():
        role = current_user.get_role()
        tender_id = form.tender_id.data
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
            return redirect(f'/{role}/tender/{tender_id}')
