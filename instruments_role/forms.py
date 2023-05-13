from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, \
    SelectField, DateField, HiddenField, IntegerField, IntegerRangeField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired, Regexp, NumberRange


class RateTenderForm(FlaskForm):
    tender_id = HiddenField(validators= [DataRequired()])
    costprice = IntegerField('Оценочная себестоимость',
                             validators=[InputRequired(message='Необходимо ввести оценочную себестоимость')])
    slider = IntegerRangeField("Оценка целесообразности участия", validators=[
        InputRequired(message='This field is required.'),
        NumberRange(min=1, max=9, message='Value must be between 1 and 9.')])
    comment = TextAreaField("Комментарий")
    submit = SubmitField("Оценить")


class DownloadDocsForm(FlaskForm):
    tender_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Скачать документы")