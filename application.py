import os
import requests, json

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("entrance.html")

@app.route("/register" , methods=["GET","POST"])
def register():
    return render_template("register.html")
    if request.method == 'POST':
        username = request.form("username")
        password = request.form("password")
        print(username)
        print(password)

        username_stored = db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username}).fetchone()
        print (username_stored)
        if username_stored is None:
            db.execute ("INSERT INTO accounts (username, password) VALUES (':username',':password')",{"username":username,"password":password})
            print("log")
            db.commit()
            return render_template("login.html")

        else:
            return render_template("error.html", message="That username already exists")

@app.route("/main" , methods=["GET","POST"])
def main():


@app.route("/logout")
def logout():
    session["account"] = []
    return render_template("entrance.html")


@app.route("/login" , methods=["GET", "POST"])
def login():
    return render_template("login.html")

    if session.get("account") is None:
        session["account"] = []
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

    if username == db.execute("SELECT * FROM accounts WHERE username = :username",
                            {"username": username}).fetchone() and password == db.execute("SELECT * FROM accounts WHERE password = :password",
                            {"password": password }).fetchone():
        return render_template("main.html", account = username)

    else:
        return render_template("error.html", message="That account doesn't exist")

@app.route("/api/<int:zipcode>")
def request(zipcode):
    if db.execute("SELECT * FROM weather WHERE zipcode = :zipcode", {"zipcode": zipcode}).rowcount == 0:
        return render_template("error.html", message="error 404: page not found")
    else:
        location = db.execute("SELECT * FROM weather WHERE zipcode = :zipcode;",{"zipcode":zipcode}).fetchall()
        return render_template("zipcodes.html", location=location)

#lattitude = db.execute("select lattitude from weather where zipcode=:zipcode",{"zipcode":zipcode}).fetchone()
#longitude = db.execute("select longitude from weather where zipcode=:zipcode",{"zipcode":zipcode}).fetchone()

#weather = requests.get("https://api.darksky.net/forecast/f8440b78453c3b6fc21855d9a12c8276/:lattitude,:longitude",{"lattitude": lattitude, "longitude": longitude }).json()
#print(json.dumps(weather["currently"], indent = 2))

#postgres://ufyogmokkpfcjp:474612b9cef13b1a1d7ddf8ce28951237aca7dece94e70bfb549deebda7be0b8@ec2-54-227-244-122.compute-1.amazonaws.com:5432/d8llvvbc60g38i