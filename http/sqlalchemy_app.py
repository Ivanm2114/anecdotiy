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
def add_anec():
    if request.method == 'GET':
        return render_template('addanecdot.html', title='Добавление анекдота')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        text = request.form['text']
        anecdot = Anecdotiy()
        text = ';'.join(text.split('\n'))
        anecdot.text = text
        anecdot.author = current_user.id
        db_sess.add(anecdot)
        db_sess.commit()
        return redirect('/')


@app.route('/deleteanecdot/<int:id>', methods=['GET', 'POST'])
def delete_anec(id):
    db_sess = db_session.create_session()
    if db_sess.query(Anecdotiy).filter(id == Anecdotiy.id).first():
        anecdot = db_sess.query(Anecdotiy).filter(id == Anecdotiy.id).first()
        db_sess.delete(anecdot)
        db_sess.commit()
        return redirect('/')


@app.route('/editanecdot/<int:id>', methods=['GET', 'POST'])
def edit_anec(id):
    db_sess = db_session.create_session()
    if db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first():
        anecdot = db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first()
        if request.method == 'GET':
            text = anecdot.text.split(';')
            return render_template('editanecdot.html', title='Добавление анекдота', text=text)
        elif request.method == 'POST':
            db_sess = db_session.create_session()
            text = request.form['text']
            text = ';'.join(text.split('\n'))
            anecdot.text = text
            db_sess.commit()
            return redirect('/')
    else:
        abort(404)

@app.route('/addlike/<int:id>')
def put_like(id):
    db_sess = db_session.create_session()
    anecdot = db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first()
    likes = anecdot.users_likes.split(';')
    dislikes = anecdot.users_dislikes.split(';')
    if (str(current_user.id) not in likes) and (str(current_user.id) not in dislikes):
        anecdot.likes += 1
        anecdot.rating += 1
        anecdot.creator.rating += 1
        likes.append(str(current_user.id))
        likes = ';'.join(likes)
        anecdot.users_likes = likes
        db_sess.commit()
        return redirect('/')
    elif str(current_user.id) in dislikes:
        anecdot.likes += 1
        anecdot.rating += 2
        anecdot.creator.rating += 2
        anecdot.dislikes -= 1
        del dislikes[dislikes.index(str(current_user.id))]
        likes.append(str(current_user.id))
        likes = ';'.join(likes)
        dislikes = ';'.join(dislikes)
        anecdot.users_likes = likes
        anecdot.users_dislikes = dislikes
        db_sess.commit()
        return redirect('/')
    else:
        return redirect('/')


@app.route('/adddislike/<int:id>')
def put_dislike(id):
    db_sess = db_session.create_session()
    anecdot = db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first()
    likes = anecdot.users_likes.split(';')
    dislikes = anecdot.users_dislikes.split(';')
    if (str(current_user.id) not in likes) and (str(current_user.id) not in dislikes):
        anecdot.dislikes += 1
        anecdot.rating -= 1
        anecdot.creator.rating -= 1
        dislikes.append(str(current_user.id))
        dislikes = ';'.join(dislikes)
        anecdot.users_dislikes = dislikes
        db_sess.commit()
        return redirect('/')
    elif str(current_user.id) in likes:
        anecdot.likes -= 1
        anecdot.creator.rating -= 2
        anecdot.rating -= 2
        anecdot.dislikes += 1
        del likes[likes.index(str(current_user.id))]
        dislikes.append(str(current_user.id))
        likes = ';'.join(likes)
        dislikes = ';'.join(dislikes)
        anecdot.users_likes = likes
        anecdot.users_dislikes = dislikes
        db_sess.commit()
        return redirect('/')
    else:
        return redirect('/')


@app.route('/main')
def all_anec():
    db_sess = db_session.create_session()
    anecdoties = db_sess.query(Anecdotiy).all()
    texts = []
    for anecdot in anecdoties:
        text = anecdot.text.split(';')
        texts.append(text)
    return render_template('anecdotiy.html', title='Все анекдоты', anecdotiy=anecdoties, texts=texts)


if __name__ == '__main__':
    db_session.global_init('db/kvn.db')
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=5000, host='127.0.0.1')
