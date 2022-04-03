from flask import Flask, render_template, request, flash, session, url_for, redirect, abort, g, make_response
import sqlite3
import os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin

# конфигурация бд
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'dhjdkjnfuefjkdsnfsdjfds'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FHSGGSDBGDRUIDNGHDYHFDGJKFDJHBF'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
"""если пользователь не имеет доступ к странице сайта,его перекидывает на авторизацию"""
login_manager.login_view = 'login'
login_manager.login_message = "Aвторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = 'success'

# максимальный размер файла который можно загрузить на сервер(1мБ)
MAX_CONTENT_LENGHT = 1024 * 1024

# регистрация blueprint
app.register_blueprint(admin, url_prefix='/admin')


@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    # представление данных в видн словаря,а не кортежа
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    # установка соединения
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    # разрыв соединения
    if hasattr(g, 'link_db'):
        g.link_db.close()


dbase = None


@app.before_request
def before_request():
    """Устанавливаем соединение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.route("/")
@login_required
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    # если данные были отправлены и введены корректно
    if form.validate_on_submit():
        user = dbase.getUserByName(form.name.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", menu=dbase.getMenu(), form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=dbase.getMenu())





@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', menu=dbase.getMenu())


@app.route("/add_post", methods=['POST', 'GET'])
@login_required
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10 and len(
                request.form['language']) > 2 and len(request.form['url']) > 2:
            author =current_user.getName()
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'],
                                    request.form['language'],author)
            if not res:
                flash("Ошибка добавления статьи", category='error')
            else:
                flash('Cтатья добавлена успешно', category="success")
        else:
            flash("Ошибка добавления статьи2", category='error')
    return render_template('add_post.html', menu=dbase.getMenu(), category=dbase.getCategory())


@app.route("/add_category", methods=['POST', 'GET'])
@login_required
def addCategory():
    if request.method == "POST":
        if len(request.form['name']) > 3:
            res = dbase.addCategory(request.form['name'])
            if not res:
                flash("Ошибка добавления категории", category='error')
            else:
                flash('Категория добавлена успешно', category="success")
        else:
            flash("Ошибка добавления категории", category='error')
    return render_template('add_category.html', menu=dbase.getMenu(), )


@app.route('/useravatar')
@login_required
def useravatar():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


@app.route("/post/<alias>")
@login_required
def ShowPost(alias):
    title, post,time,id = dbase.getPost(alias)
    if not post:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post,time =time,id=id)

@app.route("/post/<id>/delete")
def DeletePost(id):
    try:
        res = dbase.DeletePost(id)
        if not res:
            pass

    except Exception as e:
        flash("Что-то пошло не так", "error")

    return render_template('delete_note.html', menu=dbase.getMenu())

if __name__ == "__main__":
    app.run(debug=True)
