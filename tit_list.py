from flask import Flask, render_template, redirect
import requests
from data import db_session
from data.users import User
from form.user import RegisterForm, LoginForm, ContactForm
from flask_login import LoginManager, login_user, login_required, logout_user
import sys
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fgmwebgip756b]PRQE*o)FPBGF*9wgovuY($%^*%i&*87RP5DOHpgw59tu3rgergfok&jy54whigbtrusgry3urfbhi'
login_manager = LoginManager()
login_manager.init_app(app)
num_pr = '0123456789'

#  подключение к бд
def help_bd():
    db_session.global_init("bd/users.sqlite")


#  api яндекс карт
def api(x, y):
    xy = ''
    xy += str(y)
    xy += ','
    xy += str(x)
    print(xy)
    url = "http://static-maps.yandex.ru/1.x"
    params = {
        "ll": xy,
        "spn": "0.003,0.003",
        "l": "map"
    }
    response = requests.get(url, params=params)

    if not response:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "static/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    print(map_file)
    # Инициализируем pygame


#  первая страница
@app.route('/', methods=['POST', 'GET'])
def start():
    form = RegisterForm()
    form1 = ContactForm()
    if form.validate_on_submit():
        return redirect('/login')
    elif form1.validate_on_submit():
        api(form1.x.data, form1.y.data)
    return render_template('title_list.html', title='yrgehufre', form=form1)


#  окно регистрации
@app.route('/register', methods=['POST', 'GET'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        us = User(
            name=form.name.data
        )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('registration2.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        us.set_password(form.password.data)
        print(us.hashed_password)
        # print(form.name)
        db_sess.add(us)
        db_sess.commit()
        return redirect('/menu')
    return render_template('registration2.html', title='Регистрация', form=form)


#  авторизация
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/menu")
        return render_template('registration.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('registration.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


#  окно с файлом
@app.route('/menu', methods=['POST', 'GET'])
def menu():
    return render_template('menu.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def custom_404(error):
    return render_template('404.html', title="Ошибка - не найдено")


if __name__ == '__main__':
    help_bd()
    app.run(port=8080, host='127.0.0.1')
