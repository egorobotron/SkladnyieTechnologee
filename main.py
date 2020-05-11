from flask import Flask, render_template, redirect
from flask import request, make_response, session, abort, jsonify
from data import db_session, goods_api
from data.users import User
from data.goods import Goods
from  data import goods_resources
import os
import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from flask_login import LoginManager, login_user
from flask_login import login_required, logout_user, current_user

from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class GoodsForm(FlaskForm):
    name = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_fragile = BooleanField("Личное")
    place_come = TextAreaField("Откуда прибыло")
    place_going = TextAreaField("Куда отправляется")
    submit = SubmitField('Применить')


@app.route("/")
def index():
    session = db_session.create_session()
    # if current_user.is_authenticated:
    #     goods = session.query(Goods).filter(
    #         (Goods.user == current_user) | (Goods.is_fragile != True))
    # else:
    #     goods = session.query(Goods).filter(Goods.is_fragile != True)
    goods = session.query(Goods)
    return render_template("index.html", goods=goods)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/session_test/')
def session_test():
    if 'visits_count' in session:
        session['visits_count'] = session.get('visits_count') + 1
    else:
        session['visits_count'] = 1
    # дальше - код для вывода страницы
    return "Вы посещали страницу " + str(session['visits_count']) + " раз."


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
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


@app.route('/goods', methods=['GET', 'POST'])
@login_required
def add_goods():
    form = GoodsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        goods = Goods()
        goods.name = form.name.data
        goods.content = form.content.data
        goods.is_fragile = form.is_fragile.data
        goods.place_come = form.place_come.data
        goods.place_going = form.place_going.data
        current_user.goods.append(goods)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('goods.html', title='Добавление товара',
                           form=form)


@app.route('/goods/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_goods(id):
    form =GoodsForm()
    if request.method == "GET":
        session = db_session.create_session()
        goods = session.query(Goods).filter(Goods.id == id,
                                          Goods.user == current_user).first()
        if goods:
            form.name.data = goods.name
            form.content.data = goods.content
            form.is_fragile.data = goods.is_fragile
            form.place_come.data = goods.place_come
            form.place_going.data = goods.place_going
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        goods = session.query(Goods).filter(Goods.id == id,
                                          Goods.user == current_user).first()
        if goods:
            goods.name = form.name.data
            goods.content = form.content.data
            goods.is_fragile = form.is_fragile.data
            goods.place_come = form.place_come.data
            goods.place_going = form.place_going.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('goods.html', title='Редактирование новости', form=form)


@app.route('/goods_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def goods_delete(id):
    session = db_session.create_session()
    goods = session.query(Goods).filter(Goods.id == id,
                                      Goods.user == current_user).first()
    if goods:
        session.delete(goods)
        session.commit()
    else:
        abort(404)
    return redirect('/')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def main():
    DEBUG =True
    db_session.global_init("db/sklad.sqlite")
    app.register_blueprint(goods_api.blueprint)
    # для списка объектов
    api.add_resource(goods_resources.GoodsListResource, '/api/v2/goods')

    # для одного объекта
    api.add_resource(goods_resources.GoodsResource, '/api/v2/goods/<int:goods_id>')
    if DEBUG:
        port = int(os.environ.get("PORT", 8000))
        app.run(host='127.0.0.1', port=port)
    else:
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
