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
        if session.get('user') is None:
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

@app.route("/reset")
@login_required
def reset():
    db.reset_logins()
    return redirect("/")



@app.route("/pen")
def pen_index():
    page = int(request.args.get("page", 1))-1
    return render_template("pens.html", pens=db.get_pens(page=page))

@app.route("/pen/search_like")
def pen_index_search1():
    page = int(request.args.get("page", 1))-1
    term = request.args.get("q","")
    return render_template("pens.html", pens=db.search_pens_like(term, page=page))

@app.route("/pen/search_full")
def pen_index_search2():
    page = int(request.args.get("page", 1))-1
    term = request.args.get("q","")
    return render_template("pens.html", pens=db.search_pens(term, page=page))



@app.route("/pen/<int:pen_id>")
def get_pen(pen_id):
    pen = db.get_pen(pen_id)
    if pen:
        pen = dict(pen)
        pen['link'] = 'https://unsharpen.com/?s='+quote_plus(pen['name'])
        if ('user' in session):
            return render_template("pen.html", pen=pen, likes= db.get_likes(pen_id), you_like= db.get_does_like(pen_id, session['uid']))
        else:
            return render_template("pen.html", pen=pen, likes= db.get_likes(pen_id), you_like= False)
    else:
        abort(404)


### API note -- this isn't the most RESTFUL API I could immagine, but it'll serve.
@app.route("/pen/<int:pen_id>/like",methods=["GET"])
def get_pen_likes(pen_id):
    if ('user' in session):
        return jsonify({'likes': db.get_likes(pen_id), 'you_like': db.get_does_like(pen_id, session['uid'])})
    else:
        return jsonify({'likes': db.get_likes(pen_id),'you_like':False})
        

#LIKE 1

@app.route("/pen/<int:pen_id>/like0",methods=["POST"])
@login_required
def like_pen0(pen_id):
    db.like_pen(pen_id, session['uid'])
    return redirect(url_for('get_pen', pen_id=pen_id))

@app.route("/pen/<int:pen_id>/unlike0",methods=["POST"])
@login_required
def unlike_pen0(pen_id):
    db.unlike_pen(pen_id, session['uid'])
    return redirect(url_for('get_pen', pen_id=pen_id))


@app.route("/pen/<int:pen_id>/like1",methods=["POST"])
@login_required
def like_pen(pen_id):
    db.like_pen(pen_id, session['uid'])
    return jsonify({'likes': db.get_likes(pen_id), 'you_like': True})

@app.route("/pen/<int:pen_id>/like1",methods=["DELETE"])
@login_required
def unlike_pen(pen_id):
    db.unlike_pen(pen_id, session['uid'])
    return jsonify({'likes': db.get_likes(pen_id), 'you_like': False})
        

