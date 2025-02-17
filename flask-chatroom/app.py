from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
from db import SQLDatabase
import secrets
import ssl
from models import Room
# import logging
db = SQLDatabase()
db.database_setup()
# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)


app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)
room = Room()
# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    mathched =  db.check_credentials(username, password)
    if mathched == False:
        return "Error: Invalid username or password!"


    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    userFound:bool

    userFound = db.register_check(username, password)
    if userFound == False:
        return url_for('home', username=username)
    return "Error: User already exists!"


        
    

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)

    friends = db.get_friends(request.args.get("username"))
    

    return render_template("home.jinja", username=request.args.get("username"), friends=friends)



if __name__ == '__main__':
    #Load certificate and key
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain(certfile='key/zac/certificate.crt', keyfile='key/zac/myCA.key')
    socketio.run(app, ssl_context=(context))
