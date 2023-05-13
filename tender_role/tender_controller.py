import sqlite3
from functools import wraps

from flask import render_template, url_for, redirect, flash, g, abort, request
from flask_login import current_user

from FDataBase import FDataBase
# from tender_role import parser
from tender_role.forms import AddFilterForm, DeleteFilterForm, AddBanForm, DeleteBanForm, AddOptionalRulesForm, \
    SelectTender, DeleteTender
from tender_role.parser import find_new_tenders, get_filter_words, get_ban_words

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
    return True if current_user.get_role() == 'tender' else False


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


def index():
    # dbase.init_db()
    return render_template('tender/index.html', title="Интеллектуальная поддержка отбора заявок на сайте закупок",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def considered():
    select_form = SelectTender()
    delete_form = DeleteTender()
    selected_items = dbase.get_considered('отбор')
    return render_template('tender/considered.html', title='Рассматриваемые заявки',
                           selected_items=selected_items,
                           select_form=select_form,
                           delete_form=delete_form,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def select():
    select_form = SelectTender()
    if select_form.validate_on_submit():
        item_id = select_form.tender_id.data
        dbase.select_tender(item_id)
        return redirect(url_for('.considered'))
    else:
        abort(404)


def delete():
    delete_form = DeleteTender()
    if delete_form.validate_on_submit():
        item_id = delete_form.tender_id.data
        dbase.delete_tender(item_id)
        return redirect(url_for('.considered'))
    else:
        abort(404)


def selected():
    selected_items = dbase.get_selected('отбор')
    return render_template('tender/selected.html', selected_items=selected_items,
                           title="Выбранные заявки",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def rules():
    rules = get_filter_words(dbase)
    ban_rules = get_ban_words(dbase)
    optional_rules = dbase.get_optional_rules()

    add_rule_form = AddFilterForm()
    delete_rule_form = DeleteFilterForm()
    delete_rule_form.word.choices = [(word, word) for word in rules]

    add_ban_form = AddBanForm()
    delete_ban_form = DeleteBanForm()
    delete_ban_form.ban_rule.choices = [(word, word) for word in ban_rules]
    add_optional_rules_form = AddOptionalRulesForm()

    return render_template('tender/rules.html', title="База правил",
                           menu=current_user.get_menu() if current_user.is_authenticated else [],
                           rules=rules, add_rule_form=add_rule_form, delete_rule_form=delete_rule_form,
                           ban_rules=ban_rules, add_ban_form=add_ban_form, delete_ban_form=delete_ban_form,
                           optional_rules=optional_rules, add_optional_rules_form=add_optional_rules_form)


def add_rule():
    if request.method == "POST":
        new_rule = request.form['rule']
        if dbase.add_rule(new_rule):
            flash('Новое правило было успешно добавлено!')
        else:
            flash('Ошибка при добавлении правила')
        return redirect(url_for('rules'))


def add_optional_rules():
    priceFrom = int(request.form['optional_rule_priceFrom'])
    priceTo = int(request.form['optional_rule_priceTo'])
    date = request.form['optional_rule_date']
    if dbase.add_optional_rule(priceFrom, priceTo, date):
        flash('Новое правило было успешно добавлено!')
    else:
        flash('Ошибка при добавлении правила')
    return redirect(url_for('rules'))


def remove_word():
    word = request.form['word']
    if dbase.delete_filter_word(word):
        flash('Слово "{}" было успешно удалено из правил!'.format(word))
    else:
        flash('Ошибка при удалении слова')
    return redirect(url_for('rules'))


def add_ban_rule():
    new_rule = request.form['ban_rule']
    if dbase.add_ban_rule(new_rule):
        flash('Новое правило было успешно добавлено!')
    else:
        flash('Ошибка при добавлении правила!')
    return redirect(url_for('rules'))


def remove_ban_word():
    word = request.form['ban_rule']
    if dbase.delete_ban_word(word):
        flash('Слово "{}" было успешно удалено из правил!'.format(word))
    else:
        flash('Ошибка при удалении слова')
    return redirect(url_for('.rules'))


def find_tenders():
    if find_new_tenders():
        selected_items = dbase.get_considered('отбор')
        return render_template('considered.html', title='Рассматриваемые заявки', selected_items=selected_items,
                               menu=current_user.get_menu() if current_user.is_authenticated else [])
    else:
        flash("Ошибка поиска", "error")
        return redirect(url_for('.rules'))


def tender_id(id):
    tender = dbase.get_tender(id)
    if not tender or not check_role():
        print(check_role())
        abort(404)
    hr_info = dbase.get_tender_rate(id, 'hr')
    instruments_info = dbase.get_tender_rate(id, 'instruments')
    materials_info = dbase.get_tender_rate(id, 'materials')
    return render_template('tender/tender.html',
                           tender=tender,
                           title=f"Тендерная заявка номер: {id}",
                           hr_info=hr_info,
                           instruments_info=instruments_info,
                           materials_info=materials_info,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def upload_doc():
    if request.method == 'POST':
        file = request.files['file'].read()
        role = request.form['role']
        tender_id = request.form['tender_id']
        if len(file) > 0:
            try:
                res = dbase.upload_doc(file, role, tender_id)
                if not res:
                    flash("Ошибка загрузки файла", "error")
                    return redirect(f'/tender/tender/{tender_id}')
                flash("Файл загружен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
            return redirect(f'/tender/tender/{tender_id}')
        else:
            flash("Ошибка чтения файла", "error")
            return redirect(f'/tender/tender/{tender_id}')
