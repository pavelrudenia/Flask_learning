from flask import Flask, render_template, request, flash, session, url_for, redirect, abort,g
import sqlite3
import os
from FDataBase import FDataBase
app = Flask(__name__)

app.config['SECRET_KEY'] = 'FHSGGSDBGDRUIDNGHDYHFDGJKFDJHBF'
# конфигурация бд
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'dhjdkjnfuefjkdsnfsdjfds'

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
# menu = [{"name": "Установка", "url": "install-flask"},
#         {"name": "Первое приложение", "url": "first-app"},
#         {"name": "Обратная связь", "url": "contact"},
#         {"name": "Авторизация", "url": "login"}
#         ]


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    # представление данных в видн словаря,а не кортежа
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql',mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    #установка соединения
    if not hasattr(g,'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html',menu = dbase.getMenu(),posts=dbase.getPostsAnonce())


@app.teardown_appcontext
def close_db(error):
    #разрыв соединения
    if hasattr(g,'link_db'):
        g.link_db.close()


@app.route("/contact", methods=["POST", "GET"])
def contact():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        if len(request.form['username']) > 2:
            flash("Cообщение отправлено", category="success")
        else:
            flash("Ошибка отправки", category="error")

    return render_template('contact.html', menu=dbase.getMenu())


@app.route("/login", methods=["POST", "GET"])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'admin' and request.form['pass'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', menu=dbase.getMenu())


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"Профиль пользователя: {username}"


@app.errorhandler(404)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', menu=dbase.getMenu())


@app.route("/add_post",methods=['POST','GET'])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) >4 and len(request.form['post']) >10:
            res = dbase.addPost(request.form['name'],request.form['post'],request.form['url'])
            if not res:
                flash("Ошибка добавления статьи",category='error')
            else:
                flash('Cтатья добавлена успешно', category="success")
        else:
            flash("Ошибка добавления статьи",category='error')
    return render_template('add_post.html',menu =dbase.getMenu())


@app.route("/post/<alias>")
def ShowPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title,post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(),title = title,post=post)

if __name__ == "__main__":
    app.run(debug=True)
