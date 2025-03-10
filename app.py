from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

from files import delete_file
from soda_test import create_test_file, run_soda_scan, parse_test_results, validate_test_structure
from soda_config import create_config_file, validate_config_structure
from functools import wraps  # Декораторы для защиты маршрутов

app = Flask(__name__, instance_path=os.path.join(os.getcwd(), 'instance'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

CONFIG_FOLDER = 'config'
app.config['CONFIG_FOLDER'] = CONFIG_FOLDER


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)


# Декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get('logged_in'):
            flash('Сначала войдите в систему', 'warning')
            return redirect(url_for('login_form'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/create-users', methods=['POST', 'GET'])
def create_users():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        user = User.query.filter_by(login=login).first()
        if user:
            flash('Такой логин уже есть, придумай новый!', 'warning')
            return redirect(url_for('create_users'))
        user = User(login=login, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login_form'))
        except Exception as e:
            return f"Ошибка: {str(e)}"

    return render_template("create-users.html")


@app.route('/', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        if 'logout' in request.form:
            session.pop('logged_in', None)
            return redirect(url_for('login_form'))

        login = request.form.get('login').strip()
        password = request.form.get('password').strip()

        user = User.query.filter_by(login=login).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['user_id'] = user.id
            return redirect(url_for('main_page'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required  # Защита страницы
def main_page():
    test_str = session.pop('test_str', '')
    config_str = session.pop('config_str', '')

    if request.method == 'POST':

        # Загрузка текста полей в строковые переменные
        config_str = request.form['config_area']
        test_str = request.form['test_area']

        # Сохранение текста полей в сессию
        session['config_str'] = config_str
        session['test_str'] = test_str

        # Проверка на заполненность полей
        if not config_str.strip() or not test_str.strip():
            flash('Недостаточно данных', 'danger')
            return redirect(request.url)

        # Обработка конфигурации
        if validate_config_structure(config_str):
            create_config_file(config_str)
        else:
            return redirect(request.url)

        # Обработка тестов
        if validate_test_structure(test_str):
            if create_test_file(test_str):
                raw_result = run_soda_scan()
                if raw_result:
                    parsed_result = parse_test_results(raw_result)
                    return render_template("result.html", results=parsed_result, bck_btn='/home')

            return redirect(request.url)

    return render_template('index.html', test_str=test_str, config_str=config_str)


@app.route('/result')
@login_required  # Защита страницы
def result_page():
    return render_template('result.html')


if __name__ == '__main__':
    delete_file()
    app.run(debug=True)
