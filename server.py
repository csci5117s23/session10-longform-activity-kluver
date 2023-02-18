from flask import *
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from functools import wraps
import db

app = Flask(__name__)
app.secret_key = env['FLASK_SECRET']


@app.before_first_request
def setup():
    db.setup()

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

#### AUTH STUFF


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    session['uid'] = token['userinfo']['sub']
    session['email'] = token['userinfo']['email']
    session['picture'] = token['userinfo']['picture']
    if db.has_logged_in_before(session['uid']):
        return redirect("/")
    else:
        return redirect(url_for("info"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# https://flask.palletsprojects.com/en/2.2.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#### OTHER STUFF



@app.route("/")
def home():
    return render_template("main.html")

@app.route("/info")
def info():
    return render_template("info.html")

@login_required
@app.route("/reset")
def reset():
    db.reset_logins()
    return redirect("/")