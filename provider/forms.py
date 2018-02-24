from flask_wtf import FlaskForm
import wtforms
from wtforms import validators


class LoginForm(FlaskForm):
    user_id = wtforms.StringField(
        'user id',
        validators=[validators.DataRequired()],
    )
    password1 = wtforms.PasswordField(
        'password',
        validators=[validators.DataRequired()],
    )
    password2 = wtforms.PasswordField(
        'password confirm',
        validators=[
            validators.DataRequired(),
            validators.EqualTo('password1'),
        ],
    )


class AuthorizeForm(FlaskForm):
    pass
