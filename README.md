# flask-sso-demo

SSO(Single Sign On) demo web apps using Flask

## Run

Run each flask app separately:

```bash
$ export FLASK_APP=provider/application.py
$ python -m flask run --with-threads --port 5000
```

```bash
$ export FLASK_APP=client/app.py
$ python -m flask run --with-threads --port 8080
```

Note that `8080` port for `client` app is default setting.
If you change this, you might want to edit `provider/db.py` too.
Also, if you change `provider`'s default port `5000` to something else,
you might want to change `AUTHORIZE_URL` and others in `client/app.py`.
