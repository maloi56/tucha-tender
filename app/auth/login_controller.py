from app.util import dbase

from flask import render_template, redirect, flash, session, url_for
from flask_login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.util.UserLogin import UserLogin
from app.auth.forms import RegisterForm, LoginForm

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.add_user(form.role.data, form.login.data, hash)
        if res:
            flash("Пользователь успешно зарегистрирован", "success")
            return redirect(url_for('.register'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template("auth/register.html", title="Регистрация", form=form,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def login():
    if current_user.is_authenticated:
        if current_user.get_role() == 'admin':
            return redirect(url_for(".register"))
        else:
            return redirect(f"/{current_user.get_role()}/")
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByLogin(form.login.data)
        print(user)
        if user and check_password_hash(user.psw, form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            role = dbase.get_role(user.role)
            if role == "admin":
                return redirect(url_for(".register"))
            else:
                return redirect(f"/{dbase.get_role(user.role)}/")

        flash("Неверная пара логин/пароль", "error")
    return render_template("auth/login.html", title="Авторизация", form=form,
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    return redirect(url_for(".login"))
