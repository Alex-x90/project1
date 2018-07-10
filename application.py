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

notes = []

@app.route("/")
def index():
    return render_template("entrance.html")
    #initial site. redirects to login and register

@app.route("/register" , methods=["GET","POST"])
def register():
    return render_template("register.html")
    if request.method == 'POST':
        username = request.form("username")
        password = request.form("password")
        #gets username and password from form. Isn't working for some reason
        print(username)
        print(password)

    #checks if that username is already in the database. if results are none it means it isnt and it tries to store the username and password entered. otherwise it gives an error. doesnt work
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
    session["account"] = 'admin' #this is for testing purposes

    #renders the sight showing the area where the user can input data
    data_request = 1
    return render_template("main.html", account = session["account"], data_request=data_request)
    zipcode = request.form("zipcode")

    #when the user inputs a zipcode either tells them the zipcode doesnt exist or shows the information for that zipcode. for some reason when entering a zipcode the page just seems to reload
    if db.execute("SELECT * FROM weather WHERE zipcode = :zipcode", {"zipcode": zipcode}).rowcount == 0:
        return render_template("error_logged_in.html", message="sorry, that zipcode doesn't exist.")
    else:
        location = db.execute("SELECT * FROM weather WHERE zipcode = :zipcode;",{"zipcode":zipcode}).fetchone()
        data_request = 0
        lattitude = db.execute("SELECT lattitude FROM weather WHERE zipcode=:zipcode",{"zipcode":zipcode}).fetchone()
        longitude = db.execute("SELECT longitude FROM weather WHERE zipcode=:zipcode",{"zipcode":zipcode}).fetchone()
        weather = requests.get("https://api.darksky.net/forecast/f8440b78453c3b6fc21855d9a12c8276/:lattitude,:longitude",{"lattitude": lattitude, "longitude": longitude }).json()
        #print(json.dumps(weather["currently"], indent = 2))
        note = db.execute("SELECT * FROM check_in WHERE zipcode = :zipcode;",{"zipcode":zipcode}).fetchall()
        notes.append(note)

        #checks if the user has already made a note. if so doesn't display the portion of the page that would allow them to submit a new note.
        if db.execute("SELECT * FROM check_in WHERE zipcode = :zipcode and username = :username", {"zipcode": zipcode,"username":session["account"]}).rowcount == 0:
            no_comment = 1
        else:
            no_comment = 0
        #re-renders main with all the data that has been added.
        return render_template("main.html", location=location,notes=notes,no_comment=no_comment, data_request=data_request,weather=json.dumps(weather["currently"], indent = 2))

@app.route("/check_in" , methods=["GET","POST"])
def check_in():
    if request.method == "POST":
        check_in = request.form.get("check_in")
        if check_in:
        #checks if the user actually entered a note
            if db.execute("SELECT * FROM check_in WHERE zipcode = :zipcode and username = :username", {"zipcode": zipcode,"username":session["account"]}).rowcount == 0:
                db.execute("INSERT INTO check_in (username,zipcode,note) VALUES (:username,:zipcode,:check_in"),{"username":session["account"],"check_in":check_in,"zipcode":zipcode})
                db.execute("UPDATE weather SET check_ins = check_ins + 1 WHERE zipcode = :zipcode",{"zipcode":zipcode})
                #adds users check in to the list of check ins and lets the main database know someone has checked in at a zipcode

            else :
                return render_template("error_logged_in.html", message="sorry, that zipcode doesn't exist.")
        else:
            return render_template("error_logged_in.html", message="In order to check in you need to add a note.")
    return render_template("main.html", notes=notes)

@app.route("/logout")
def logout():
    #logs the user out by deleting informtion from the session that stores their information
    session["account"] = []
    return render_template("entrance.html")

@app.route("/login" , methods=["GET", "POST"])
def login():
    return render_template("login.html")

    #sets up the account session so that if the user logs in the website can store their username and display it.
    if session.get("account") is None:
        session["account"] = []
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

    #checks if the users username and password match up with a username and password pair in the database. This doesn't work yet
    if db.execute("SELECT * FROM accounts WHERE username = :username and password = :password", {"username": username,"password": password }).fetchone() != None
        session["account"] = [username]
        return render_template("main.html", account = session["account"])

    else:
        return render_template("error.html", message="That account doesn't exist")


@app.route("/api/<int:zipcode>")
def request(zipcode):
    #gets the information about the zipcode the user entered. Dont know how to properly set up the json output that is asked for
    if db.execute("SELECT * FROM weather WHERE zipcode = :zipcode", {"zipcode": zipcode}).rowcount == 0:
        return render_template("error.html", message="error 404: page not found")
    else:
        location = db.execute("SELECT * FROM weather WHERE zipcode = :zipcode;",{"zipcode":zipcode}).fetchall()
        return render_template("zipcodes.html", location=location)

#postgres://ufyogmokkpfcjp:474612b9cef13b1a1d7ddf8ce28951237aca7dece94e70bfb549deebda7be0b8@ec2-54-227-244-122.compute-1.amazonaws.com:5432/d8llvvbc60g38i