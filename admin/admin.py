import sqlite3

from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g
from flask_login import login_required
import psycopg2.extras
from FDataBase import FDataBase

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список заметок'},
        {'url': '.logout', 'title': 'Выйти'}]

db = None


@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    # g контекст приложения
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


def login_admin():
    session['admin_logged'] = 1


def isLogged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)


@login_required
@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')


@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))
    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')


@login_required
@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login'))


@login_required
@admin.route('/list-pubs')
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(f"SELECT title, text,author,time, url FROM posts")
            list = cur.fetchall()
            print(list)
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listpubs.html', title='Список заметок', menu=menu, list=list, )


@login_required
@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:

            cur =db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
            print(list)

        except Exception as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listusers.html', title='Список пользователей', menu=menu, list=list)


@admin.route("/<author>/delete")
def DeleteUser(author):
    if db:
        try:
            cur =db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            author_a  =author.replace("<","")
            author_b = author_a.replace(">", "")
            print(author_b)
            cur.execute(f"Delete from users where name ='{author_b}'")
            db.commit()

        except sqlite3.Error as e:
            print("Ошибка удаления пользователей  из БД " + str(e))

    return render_template('admin/deleteuser.html',title="Пользователь удален &#10060")

