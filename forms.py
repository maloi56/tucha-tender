from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    login = StringField("auth: ", validators=[DataRequired()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default = False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    role = StringField("Роль: ", validators=[DataRequired()])
    login = StringField("Логин: ", validators=[DataRequired()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")


class AddFilterForm(FlaskForm):
    rule = StringField("Новый фильтр", validators=[DataRequired()])
    submit = SubmitField("Добавить фильтр")


class DeleteFilterForm(FlaskForm):
    word = SelectField("Фильтр на удаление", validators=[DataRequired()])
    submit = SubmitField("Удалить фильтр")


class AddBanForm(FlaskForm):
    ban_rule = StringField("Новое исключение", validators=[DataRequired()])
    submit = SubmitField("Добавить новое исключение")


class DeleteBanForm(FlaskForm):
    ban_rule = SelectField("Исключение на удаление", validators=[DataRequired()])
    submit = SubmitField("Удалить исключение")


class AddOptionalRulesForm(FlaskForm):
    optional_rule_priceFrom = StringField(render_kw={"placeholder": "Начальная цена"}, validators=[DataRequired()])
    optional_rule_priceTo = StringField(render_kw={"placeholder": "Максимальная цена"}, validators=[DataRequired()])
    optional_rule_date = DateField(validators=[DataRequired()])
    submit = SubmitField("Обновить")
