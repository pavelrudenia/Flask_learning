from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Email, DataRequired, Length, EqualTo
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    name = StringField("Логин", validators=[DataRequired(), Length(min=4, max=20)])
    psw = PasswordField("Пароль:", validators=[DataRequired(), Length(min=4, max=20,message="Пароль должен быть от 4 до 20 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=20, message="Имя должно быть от 4 до 20 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=20, message="Пароль должен быть от 4 до 20 символов")])
    psw2 = PasswordField("Повторите: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")