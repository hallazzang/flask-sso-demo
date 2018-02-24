from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode

import flask

from .forms import AuthorizeForm
from .db import registered_apps
from .utils import *


@app.route('/sso/authorize', methods=['GET', 'POST'])
def authorize():
    app_id = flask.request.args.get('app_id')
    redirect_uri = flask.request.args.get('redirect_uri')
    scope = flask.request.args.get('scope')

    if not all((app_id, redirect_uri, scope)):
        return 'Missing parameters', 400

    if app_id not in registered_apps:
        return 'There is no such app', 400

    if not is_child_url(registered_apps[app_id]['url'], redirect_uri):
        return 'Invalid redirect URI', 400

    if not is_valid_scope(scope):
        return 'Invalid scope', 400

    user = get_login_user()
    if not user:
        return redirect_safe(flask.url_for('login', next=flask.request.url))

    form = AuthorizeForm()
    if form.validate_on_submit():
        auth_token = serializer.dumps({
            'type': 'auth_token',
            'user_id': user['id'],
            'app_id': app_id,
            'scope': scope,
        })

        return flask.redirect(set_qs(redirect_uri, auth_token=auth_token))

    return flask.render_template(
        'authorize.html', app_name=registered_apps[app_id]['name'],
        user_name=user['name'], form=form, scope=scope.split(','))


@app.route('/sso/exchange_token', methods=['POST'])
def exchange_token():
    auth_token = flask.request.form.get('auth_token')
    app_secret = flask.request.form.get('app_secret')

    if not all((auth_token, app_secret)):
        return flask.jsonify(error_msg='Missing parameters'), 400

    try:
        info = serializer.loads(auth_token, max_age=10)
    except itsdangerous.BadData:
        return flask.jsonify(error_msg='Invalid auth token'), 400

    if info.get('type') != 'auth_token':
        return flask.jsonify(error_msg='Invalid token type'), 400

    if info['app_id'] not in registered_apps:
        return flask.jsonify(error_msg='There is no such app'), 400

    if app_secret != registered_apps[info['app_id']]['secret']:
        return flask.jsonify(error_msg='Mismatching app secret'), 400

    info['type'] = 'access_token'
    access_token = serializer.dumps(info)

    return flask.jsonify(access_token=access_token)


@app.route('/api/user/profile')
def profile():
    if 'Authorization' not in flask.request.headers:
        return flask.jsonify(error_msg='No authorization header'), 400

    access_token = flask.request.headers['Authorization']
    try:
        info = serializer.loads(access_token, max_age=30)
    except itsdangerous.SignatureExpired:
        return flask.jsonify(error_msg='Access token expired'), 400
    except itsdangerous.BadData:
        return flask.jsonify(error_msg='Invalid access token'), 400

    if info['type'] != 'access_token':
        return flask.jsonify(error_msg='Invalid token type'), 400

    user = users.get(info['user_id'])
    if not user:
        # Yes it's possible scenario, when the user has unregistered
        return flask.jsonify(error_msg='There is no such user'), 401

    return flask.jsonify(user_id=user['id'], user_name=user['name'])
