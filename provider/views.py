import flask

from .forms import LoginForm
from .db import users
from .utils import *


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_login_user():
        flask.flash('You are already logged in', 'info')
        return redirect_safe(flask.url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data.strip()
        password = form.password1.data.strip()

        next = flask.request.args.get('next')

        if user_id not in users:
            flask.flash('There is no such user', 'error')
            return redirect_safe(flask.url_for('login', next=next))

        if password != users[user_id]['password']:
            flask.flash('Login failed', 'error')
            return redirect_safe(flask.url_for('login', next=next))

        # Logging the user in
        flask.session['user_id'] = user_id

        return redirect_safe(next or flask.url_for('index'))

    return flask.render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if not get_login_user():
        flask.flash('You are not logged in', 'error')
        return redirect_safe(flask.url_for('index'))

    del flask.session['user_id']
    flask.flash('Successfully logged out', 'info')

    return redirect_safe(flask.url_for('index'))
