import datetime
import os

from flask import Flask, request, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.anecdot import Anecdotiy
from data.users import User
from data.category import Category
from forms.user import RegisterForm, LoginForm
from forms.categories import CreateCategory, EditCategory

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
        text = request.form['text'].strip()
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
        cats = db_sess.query(Category).all()
        for cat in cats:
            if cat.anecdoties:
                anecdoties_id = cat.anecdoties.split(',')
                if str(id) in anecdoties_id:
                    print(anecdoties_id)
                    anecdoties_id.pop(anecdoties_id.index(str(id)))
                    anecdoties_id = ','.join(anecdoties_id)
                    cat.anecdoties = anecdoties_id
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
            text = request.form['text'].strip()
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


@app.route('/addlikecat/<int:id>/<int:cat_id>')
def put_like_cat(id, cat_id):
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
        return redirect(f'/viewcategory/{cat_id}')
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
        return redirect(f'/viewcategory/{cat_id}')
    else:
        return redirect(f'/viewcategory/{cat_id}')


@app.route('/adddislikecat/<int:id>/<int:cat_id>')
def put_dislike_cat(id, cat_id):
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
        return redirect(f'/viewcategory/{cat_id}')
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
        return redirect(f'/viewcategory/{cat_id}')
    else:
        return redirect(f'/viewcategory/{cat_id}')


@app.route('/main')
def all_anec():
    db_sess = db_session.create_session()
    anecdoties = db_sess.query(Anecdotiy).all()
    texts = []
    for anecdot in anecdoties:
        text = anecdot.text.split(';')
        texts.append(text)
    return render_template('anecdotiy.html', title='Все анекдоты', anecdotiy=anecdoties, texts=texts)


@app.route('/categories')
def all_cats():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    return render_template('categories.html', title='Все категории', categories=categories)


@app.route('/addcategory', methods=['GET', 'POST'])
def add_cat():
    form = CreateCategory()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        cat = Category()
        cat.name = form.name.data
        if form.anecdots_id.data:
            cat.anecdoties = form.anecdots_id.data
        else:
            cat.anecdoties = ' '
        db_sess.add(cat)
        db_sess.commit()
        id = db_sess.query(Category).filter(Category.name == form.name.data).first().id
        return redirect(f'/viewcategory/{id}')
    return render_template('addcategory.html', title='Добавление категории', form=form)


@app.route('/editcategory/<int:id>', methods=['GET', 'POST'])
def edit_cat(id):
    form = EditCategory()
    db_sess = db_session.create_session()
    cat = db_sess.query(Category).filter(Category.id == id).first()
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.anecdoties = form.anecdots_id.data
        db_sess.commit()
        return redirect(f'/viewcategory/{id}')
    else:
        form.name.data = cat.name
        form.anecdots_id.data = cat.anecdoties
    return render_template('editcategory.html', title='Изменение категории', form=form)


@app.route('/deletecategory/<int:id>', methods=['GET', 'POST'])
def delete_cat(id):
    db_sess = db_session.create_session()
    if db_sess.query(Category).filter(id == Category.id).first():
        cat = db_sess.query(Category).filter(id == Category.id).first()
        db_sess.delete(cat)
        db_sess.commit()
        return redirect('/categories')


@app.route('/viewcategory/<int:id>')
def view_cat(id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == id).first()
    anecdoties = []
    texts = []
    if category.anecdoties:
        anecdoties_id = category.anecdoties.split(',')
        for id in anecdoties_id:
            anec = db_sess.query(Anecdotiy).filter(Anecdotiy.id == id).first()
            if anec:
                text = anec.text.split(';')
                texts.append(text)
                anecdoties.append(anec)
    return render_template('viewcategory.html', category=category, anecdoties=anecdoties, texts=texts)


@app.route('/addanecdotto/<int:id>', methods=['GET', 'POST'])
def add_anec_to(id):
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
        anec = db_sess.query(Anecdotiy).filter(Anecdotiy.text == text).first()
        cat = db_sess.query(Category).filter(Category.id == id).first()
        if cat.anecdoties:
            anecdoties_id = cat.anecdoties.split(',')
            anecdoties_id.append(str(anec.id))
            anecdoties_id = ','.join(anecdoties_id)
        else:
            anecdoties_id = str(anec.id)
        cat.anecdoties = anecdoties_id
        db_sess.commit()
        return redirect(f'/viewcategory/{id}')


@app.route('/rating')
def rating():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    users.sort(key=lambda x: x.rating, reverse=True)
    return render_template('rating.html', title='Рейтинг пользователей', users=users)


if __name__ == '__main__':
    db_session.global_init('db/mars_explorer.db')
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=5000, host='127.0.0.1')
