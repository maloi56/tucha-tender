from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    role = SelectField ("Роль", validators=[DataRequired()], choices=[("hr", "Отдел кадров"), ("instruments", "Инструментальный отдел"),
("materials", "Отдел материального учета"), ("tender", "Тендерный отдел"), ("director", "Директор")])
    login = StringField("Логин: ", validators=[DataRequired()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")


class LoginForm(FlaskForm):
    login = StringField("Логин: ", validators=[DataRequired()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")
