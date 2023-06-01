import time
import math

from model import db, Selected, Roles, Users, FilterWords, BanWords, Rules, Rating
from datetime import datetime

from werkzeug.security import generate_password_hash


def insert_tenders(res):
    try:
        Selected.query.filter(Selected.status == 'отбор', Selected.date <= datetime.today()).delete()
        for key, value in res.items():
            if Selected.query.get(key) is None:
                value['status'] = 'отбор'
                selected_obj = Selected(**value)
                db.session.add(selected_obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def get_department_doc(tender_id, role):  # ПОСМОТРЕТЬ ДЖОИНЫ
    try:
        role_obj = Roles.query.filter_by(name=role).first()
        if not role_obj:
            print("Роль не найдена")
            return False

        rating = Rating.query.filter_by(tender=tender_id, role=role_obj.id).first()
        if not rating:
            return False

        return rating.document
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def upload_doc(doc, role, tender_id):
    try:
        role_obj = Roles.query.filter_by(name=role).first()
        if not role_obj:
            print("Роль не найдена")
            return False

        rating = Rating.query.filter_by(tender=tender_id, role=role_obj.id).first()
        if not rating:
            print("Рейтинг не найден")
            return False

        rating.document = doc
        db.session.commit()
        return True
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def get_tender_rate(tender_id, role):
    try:
        rating = db.session.query(Rating, Roles).select_from(Rating).join(Roles, Rating.role == Roles.id).filter(
            Rating.tender == tender_id, Roles.name == role).first()
        if not rating:
            return False
        return rating
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def set_status(tender_id, status):
    try:
        tender = Selected.query.get(tender_id)
        if not tender:
            print("Тендер не найден")
            return False

        tender.status = status
        db.session.commit()
    except Exception as e:
        print("Ошибка БД в статусе: " + str(e))
        return False
    return True


def rate_tender(role, tender_id, cost_price, comment, rate):
    try:
        role_obj = Roles.query.filter_by(name=role).first()
        if not role_obj:
            print("Роль не найдена")
            return False

        rating = Rating.query.filter_by(tender=tender_id, role=role_obj.id).first()
        if not rating:
            print("Рейтинг не найден")
            return False

        rating.rate = rate
        rating.comment = comment
        rating.costprice = cost_price

        db.session.commit()
    except Exception as e:
        print("Ошибка добавления пользователя в БД: " + str(e))
        return False
    return True


def get_tender(tender_id):
    try:
        tender = Selected.query.filter_by(id=tender_id).filter(Selected.status != 'отбор').first()
        if not tender:
            return False
        return tender
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def get_role(user_id):
    try:
        role = Roles.query.filter_by(id=user_id).first()
        if not role:
            print("Роль не найдена")
            return False
        return role.name
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))

    return False


def getUserByLogin(login):
    try:
        user = Users.query.filter_by(login=login).first()
        if not user:
            print("Пользователь не найден")
            return False
        return user
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))

    return False


def getUser(user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            print("Пользователь не найден")
            return False

        role_name = Roles.query.filter_by(id=user.role).first()
        if not role_name:
            print("Роль пользователя не найдена")
            return False

        return {'id': user.id, 'role': role_name.name, 'login': user.login, 'psw': user.psw, 'time': user.time}
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))

    return False


def delete_ban_word(word):
    try:
        BanWords.query.filter_by(word=word).delete()
        db.session.commit()
        return True
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def add_ban_rule(new_rule):
    try:
        ban_rule = BanWords(word=new_rule)
        db.session.add(ban_rule)
        db.session.commit()
        return True
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def delete_filter_word(word):
    try:
        FilterWords.query.filter_by(word=word).delete()
        db.session.commit()
        return True
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def add_optional_rule(priceFrom, priceTo, date):
    try:
        rule = Rules.query.first()
        if not rule:
            rule = Rules(priceFrom=priceFrom, priceTo=priceTo, date=date)
            db.session.add(rule)
        else:
            rule.priceFrom = priceFrom
            rule.priceTo = priceTo
            print(type(date))
            print(date)
            rule.date = date
        db.session.commit()
        return True
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
    return False


def add_user(role, login, hpsw):
    try:
        existing_user = Users.query.filter_by(login=login).first()
        if existing_user:
            print("Пользователь с таким login уже существует")
            return False

        role_obj = Roles.query.filter_by(name=role).first()
        if not role_obj:
            print("Роль не найдена")
            return False

        tm = math.floor(time.time())
        user = Users(role=role_obj.id, login=login, psw=hpsw, time=tm)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))
        return False
    return True


def add_rule(new_rule):
    try:
        rule = FilterWords(word=new_rule)
        db.session.add(rule)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))
    return False


def get_optional_rules():
    try:
        res = Rules.query.all()
        return res
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))


def get_ban_words():
    try:
        res = BanWords.query.all()
        return res
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))


def get_filter_words():
    try:
        res = FilterWords.query.all()
        return res
    except Exception as e:
        print("Ошибка получения данных из БД: " + str(e))


def delete_tender(tender_id):
    try:
        selected = Selected.query.get(tender_id)
        if selected is not None:
            selected.status = 'Удалено'
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def select_tender(tender_id):
    try:
        selected = Selected.query.get(tender_id)
        if selected is not None:
            selected.status = 'на рассмотрении'

            roles = Roles.query.filter(Roles.name != 'tender', Roles.name != 'director', Roles.name != 'admin').all()
            for role in roles:
                rating = Rating(rate=0, costprice=0, role=role.id, tender=tender_id)
                db.session.add(rating)

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def get_roles():
    try:
        res = Roles.query.all()
        return res
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def get_selected(status):
    try:
        res = Selected.query.filter(Selected.status != status).all()
        return res
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def get_considered_count(status):
    try:
        res = Selected.query.filter_by(status=status).count()
        return res
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def get_considered(status):
    try:
        res = Selected.query.filter_by(status=status).all()
        return res
    except Exception as e:
        db.session.rollback()
        print("Ошибка получения данных из БД: " + str(e))


def init_admin():
    hash = generate_password_hash('admin')
    add_user('admin', 'admin', hash)
