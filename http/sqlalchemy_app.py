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
from forms.jobs import CreateJob, EditJob
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
        if db_sess.query(User).filter(User.email == form.Login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.Name.data,
            email=form.Login.data,
            surname=form.Surname.data,
            age=form.Age.data,
            position=form.Position.data,
            speciality=form.Speciality.data,
            address=form.Address.data,
            hometown=form.Hometown.data

        )
        user.set_password(form.Password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            user.check_password(form.password.data)
            if user and user.check_password(form.password.data):
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


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/addjob', methods=['GET', 'POST'])
def add_job():
    form = CreateJob()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        job = Jobs(
            team_leader=form.team_leader.data,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data

        )
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('create_job.html', title='Добавление работы', form=form)


@app.route('/deletejob/<int:id>', methods=['GET', 'POST'])
def delete_job(id):
    db_sess = db_session.create_session()
    if db_sess.query(Jobs).filter(id == Jobs.id).first():
        job = db_sess.query(Jobs).filter(id == Jobs.id).first()
        db_sess.delete(job)
        db_sess.commit()
        return redirect('/')


@app.route('/editjob/<int:id>', methods=['GET', 'POST'])
def edit_job(id):
    form = EditJob()
    db_sess = db_session.create_session()
    if db_sess.query(Jobs).filter(id == Jobs.id).first():
        job = db_sess.query(Jobs).filter(id == Jobs.id).first()
        if form.validate_on_submit():
            if current_user.id == 1 or current_user.id == job.team_leader:
                job.job = form.job.data
                job.work_size = form.work_size.data
                job.collaborators = form.collaborators.data
                job.is_finished = form.is_finished.data
                db_sess.commit()
                return redirect('/')
            else:
                return render_template('edit_job.html', title='Изменение', form=form,
                                       message='У пользователя нет доступа')

        form.job.data = job.job
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished
        return render_template('edit_job.html', title='Изменение', form=form)
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




@app.route('/departments')
def deps():
    db_sess = db_session.create_session()
    return render_template('departments.html', deps=db_sess.query(Department).all())




if __name__ == '__main__':
    db_session.global_init('db/kvn.db')
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=5000, host='127.0.0.1')
