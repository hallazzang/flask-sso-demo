from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
import flask
import itsdangerous

from .application import app
from .db import users

serializer = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])


def get_login_user():
    if 'user_id' in flask.session:
        return users.get(flask.session['user_id'])
    else:
        return None


def redirect_safe(url):
    return flask.redirect(url)  # NOTE: Temporary implementation


def is_child_url(parent_url, child_url):
    _, netloc1, path1, _, _ = urlsplit(parent_url)
    _, netloc2, path2, _, _ = urlsplit(child_url)

    return netloc1 == netloc2 and path2.startswith(path1)


def is_valid_scope(scope):
    return True  # NOTE: Temporary implementation


def set_qs(url, **kwargs):
    scheme, netloc, path, query, fragment = urlsplit(url)
    q = parse_qs(query)
    q.update(kwargs)
    query = urlencode(q, doseq=True)
    return urlunsplit((scheme, netloc, path, query, fragment))
