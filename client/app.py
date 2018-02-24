from urllib.parse import urlencode, urljoin

import flask

import requests

app = flask.Flask(__name__)

AUTHORIZE_URL = 'http://127.0.0.1:5000/sso/authorize'
EXCHANGE_TOKEN_URL = 'http://127.0.0.1:5000/sso/exchange_token'
API_PROFILE_URL = 'http://127.0.0.1:5000/api/user/profile'
APP_ID = 'TESTAPP'
APP_SECRET = 'APPSECRET'


@app.route('/')
def index():
    qs = urlencode({
        'app_id': APP_ID,
        'redirect_uri': flask.url_for('callback', _external=True),
        'scope': 'read,write',
    })
    auth_url = '%s?%s' % (AUTHORIZE_URL, qs)

    access_token = flask.request.cookies.get('access_token')
    if not access_token:
        return '<a href="%s">Authorize</a>' % auth_url
    else:
        headers = {'Authorization': access_token}
        r = requests.get(API_PROFILE_URL, headers=headers)
        body = r.json()
        if r.status_code != 200:
            return '''
                Authorization failed(Reason: %s) <a href="%s">Authorize</a>
            ''' % (body['error_msg'], auth_url)

        return 'Hello, %s! <a href="%s">Logout</a>' % (
            body['user_name'], flask.url_for('logout'))


@app.route('/logout')
def logout():
    resp = flask.make_response(flask.redirect(flask.url_for('index')))
    resp.set_cookie('access_token', '', expires=0)
    return resp


@app.route('/sso/callback')
def callback():
    auth_token = flask.request.args.get('auth_token')
    data = {
        'app_secret': APP_SECRET,
        'auth_token': auth_token,
    }
    r = requests.post(EXCHANGE_TOKEN_URL, data=data)
    body = r.json()
    if r.status_code != 200:
        return 'Authorization failed(Reason: %s)' % body['error_msg'], 400

    resp = flask.make_response(flask.redirect(flask.url_for('index')))
    resp.set_cookie('access_token', body['access_token'], httponly=True)

    return resp
