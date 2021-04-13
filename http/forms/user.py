from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    Login = StringField('Login', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Valid_password = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Admin = BooleanField('Admin')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    Login = StringField('Логин', validators=[DataRequired()])
    Password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
