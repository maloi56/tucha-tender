from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, \
    SelectField, DateField, HiddenField, IntegerField, IntegerRangeField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired, Regexp, NumberRange
from wtforms.widgets import HiddenInput


class AddFilterForm(FlaskForm):
    rule = StringField("Новый фильтр", validators=[DataRequired()])
    submit = SubmitField("Добавить новый фильтр")


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


class SelectTenderForm(FlaskForm):
    # tender_id = HiddenField(validators=[DataRequired()])
    tender_id = StringField(validators=[DataRequired()])
    submit = SubmitField("Выбрать")


class DeleteTenderForm(FlaskForm):
    tender_id = StringField(validators=[DataRequired()])
    submit = SubmitField("Удалить")


class UploadDocForm(FlaskForm):
    tender_id = StringField(validators=[DataRequired()])
    role = StringField(validators=[DataRequired()])
    file = FileField()
    submit = SubmitField("Загрузить")


class DownloadDocsForm(FlaskForm):
    doc_href = HiddenField()
    submit = SubmitField("Скачать документы")
