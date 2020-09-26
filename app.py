from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    got_request_exception,
)
from database.database_functions import (
    insert_into_users,
    insert_into_user_data,
    get_user,
)
import logging
from configparser import ConfigParser
from flask.json import JSONEncoder
from datetime import datetime
import os
from authlib.flask.client import OAuth
from constants import *
from six.moves.urllib.parse import urlencode
from functools import wraps
from utils import handle_input, send_text
import json

# Getting the environment settings
parser = ConfigParser()
parser.read("dev.ini")
HOST = parser.get("website", "host")
PORT = int(parser.get("website", "port"))

debug_status = parser.get("settings", "debug")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler("error.log")
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# adding the handlers to the logger
logger.addHandler(handler)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask(__name__, template_folder="client/templates", static_folder="client/static")
app.json_encoder = CustomJSONEncoder
app.secret_key = "supersekrit"
oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + "/oauth/token",
    authorize_url=AUTH0_BASE_URL + "/authorize",
    client_kwargs={"scope": "openid profile email",},
)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if PROFILE_KEY not in session:
            return redirect("/login")
        return f(*args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated


def has_accepted(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if len(has_accepted_beta(session[JWT_PAYLOAD]["name"])):
            return redirect("/agreement")
        return f(*args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated


@app.route("/callback")
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get("userinfo")
    userinfo = resp.json()

    session[JWT_PAYLOAD] = userinfo
    session[PROFILE_KEY] = {
        "user_id": userinfo["sub"],
        "name": userinfo["name"],
        "picture": userinfo["picture"],
    }
    return redirect("/")


@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri="http://" + request.host + "/callback")


@app.route("/logout")
def logout():
    session.clear()
    params = {"returnTo": url_for("home", _external=True), "client_id": AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))


@app.route("/")
@login_required
def render_home():
    user = get_user(session[JWT_PAYLOAD]["name"])
    print(user[0]["id"])
    if len(user) == 0:
        insert_into_users(session[JWT_PAYLOAD]["name"])
    return render_template("bot.html"), 200


@app.route("/input", methods=["GET", "POST"])
def add_job():
    """
    Function that handles the API calls
    :return: 200 HTTP code
    """
    data = request.form  # Extracting json da   ta given to the api
    print("input", data["text"])
    query = data["text"]
    return send_text(handle_input(query))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=debug_status, port=PORT, threaded=True)
