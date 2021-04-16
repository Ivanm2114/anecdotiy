from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired


class CreateCategory(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    anecdots_id = StringField('Номера анекдотов для подборки(Вводить через запятую)', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class EditCategory(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    anecdots_id = StringField('Номера анекдотов для подборки(Вводить через запятую)', validators=[DataRequired()])
    submit = SubmitField('Изменить')


