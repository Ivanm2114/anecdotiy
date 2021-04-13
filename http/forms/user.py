from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    Login = StringField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Valid_password = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Age = IntegerField('Age', validators=[DataRequired()])
    Position = StringField('Position', validators=[DataRequired()])
    Speciality = StringField('Speciality', validators=[DataRequired()])
    Address = StringField('Address', validators=[DataRequired()])
    Hometown = StringField("Hometown", validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
