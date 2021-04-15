import datetime
import requests
import os
import sys
from flask import Flask, request, render_template, make_response, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from requests import get
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.anecdot import Anecdotiy
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.departments import CreateDepartment, EditDepartment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def f():
    if current_user.is_authenticated:
        return redirect('/main')
    else:
        return render_template('motivate_register.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.Password.data != form.Valid_password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.Login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.Name.data,
            login=form.Login.data,
            surname=form.Surname.data,
            admin=form.Admin.data
        )
        user.set_password(form.Password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.Login.data).first()
        if user:
            user.check_password(form.Password.data)
            if user and user.check_password(form.Password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addanecdot', methods=['GET', 'POST'])
def add_job():
    if request.method == 'GET':
        return render_template('addanecdot.html', title='Добавление анекдота')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        text = request.form['text']
        anecdot = Anecdotiy()
        anecdot.text = text
        anecdot.author = current_user.id
        db_sess.add(anecdot)
        db_sess.commit()
        return redirect('/')


@app.route('/deleteanecdot/<int:id>', methods=['GET', 'POST'])
def delete_job(id):
    db_sess = db_session.create_session()
    if db_sess.query(Anecdotiy).filter(id == Anecdotiy.id).first():
        anecdot = db_sess.query(Anecdotiy).filter(id == Anecdotiy.id).first()
        db_sess.delete(anecdot)
        db_sess.commit()
        return redirect('/')


@app.route('/editanecdot/<int:id>', methods=['GET', 'POST'])
def edit_job(id):
    db_sess = db_session.create_session()
    if db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first():
        anecdot = db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first()
        if request.method == 'GET':
            request.form['text'] = anecdot.text
            return render_template('editanecdot.html', title='Добавление анекдота')
        elif request.method == 'POST':
            db_sess = db_session.create_session()
            text = request.form['text']
            anecdot = Anecdotiy()
            anecdot.text = text
            anecdot.author = current_user.id
            db_sess.add(anecdot)
            db_sess.commit()
            return redirect('/')
    else:
        abort(404)


@app.route('/adddepartment', methods=['GET', 'POST'])
def add_dep():
    form = CreateDepartment()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        dep = Department(
            title=form.title.data,
            chief=form.chief.data,
            members=form.members.data,
            email=form.email.data
        )
        db_sess.add(dep)
        db_sess.commit()
        return redirect('/departments')
    return render_template('create_department.html', title='Добавление департамента', form=form)


@app.route('/editdepartment/<int:id>', methods=['GET', 'POST'])
def edit_dep(id):
    form = EditDepartment()
    db_sess = db_session.create_session()
    if db_sess.query(Department).filter(id == Department.id).first():
        dep = db_sess.query(Department).filter(id == Department.id).first()
        if form.validate_on_submit():
            print(current_user.id)
            if current_user.id == 1 or current_user.id == dep.chief:
                dep.title = form.title.data
                dep.members = form.members.data
                dep.email = form.email.data
                print(dep)
                db_sess.commit()
                return redirect('/departments')
            else:
                return render_template('edit_department.html', title='Изменение', form=form,
                                       message='У пользователя нет доступа')

        form.title.data = dep.title
        form.members.data = dep.members
        form.email.data = dep.email
        return render_template('edit_department.html', title='Изменение', form=form)
    else:
        abort(404)


@app.route('/main')
def all_anec():
    db_sess = db_session.create_session()
    return render_template('anecdotiy.html', title='Все анекдоты', anecdotiy=db_sess.query(Anecdotiy).all())


if __name__ == '__main__':
    db_session.global_init('db/kvn.db')
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=5000, host='127.0.0.1')
