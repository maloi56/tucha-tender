from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo


class DirectorDocsForm(FlaskForm):
    doc_href = HiddenField()
    submit = SubmitField("Скачать документы")


class DirectorStatusForm(FlaskForm):
    doc_href = HiddenField()
    status = SelectField(validators=[DataRequired()], choices=[('принято', 'Принять'), ('отклонено', 'Отклонить'),
                                                                ('на рассмотрении', 'Отправить на рассмотрение')])
    submit = SubmitField("Установить статус")