from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, \
    SelectField, DateField, HiddenField, IntegerField, IntegerRangeField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired, Regexp, NumberRange


class RateTenderForm(FlaskForm):
    tender_id = HiddenField(validators=[DataRequired()])
    costprice = IntegerField('Оценочная себестоимость',
                             validators=[InputRequired(message='Необходимо ввести оценочную себестоимость')])
    select = SelectField(validators=[
        InputRequired(message='This field is required.')],
        choices=[('', 'Оценка целесообразности участия')] + [(str(i), str(i)) for i in range(1, 10)])
    comment = TextAreaField("Комментарий")
    submit = SubmitField("Оценить")


class DownloadDocsForm(FlaskForm):
    tender_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Скачать документ")
