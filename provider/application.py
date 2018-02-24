import random
import string

import flask

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

# Import these modules later to prevent cyclic import problem
from . import views
from . import sso_views
from .utils import *


@app.context_processor
def inject_user():
    return {'user': get_login_user()}
