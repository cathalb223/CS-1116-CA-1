from flask import Flask, render_template, session, redirect, url_for, g, request
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm, CreateForm, CharacterForm, Create_campaignForm, FriendForm
from functools import wraps

"""Hello! Thank you for your time grading this assignment. 
Your username and login is Derek Bridge and 123 respectively.
To test friend requests John Doe's password is 123.
To become friends a request must be sent from both parties """


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "Something-something-something"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id",None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        db = get_db()
        conflict = db.execute("""SELECT * FROM users
                       WHERE user_id = ?""", (user_id,)).fetchone()
            
        if conflict is not None:
            form.user_id.errors.append("User ID conflict")
        else:

            db.execute("""INSERT INTO users (user_id, password)
                              VALUES (?, ?);""", (user_id, generate_password_hash(password) ))
            db.commit()
            return redirect(url_for("login"))
        


    return render_template("registration_form.html", 
                           form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        
        db = get_db()
        matching_user = db.execute("""SELECT * FROM users
                       WHERE user_id = ?""", (user_id,)).fetchone()
            
        if matching_user is None:
            form.user_id.errors.append("Unknown User ID")
        elif not check_password_hash(matching_user["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["user_id"] = user_id
            return redirect(url_for("index"))

    return render_template("login_form.html", 
                           form=form)

@app.route("/Create", methods=["GET", "POST"])
@login_required
def Create():
    form = CreateForm()

    if form.validate_on_submit():
        CharName = form.CharName.data
        species = form.species.data
        level = form.level.data
        className = form.className.data

        
        db = get_db()
        db.execute("""INSERT INTO characters (name, species, level, class, user_id)
                              VALUES (?, ?, ?, ?, ?);""", (CharName,species,level,className,session["user_id"]))
        db.commit()
        
        return redirect(url_for("Characters"))


    return render_template("character_create_form.html", 
                           form=form)



@app.route("/Characters", methods=["GET", "POST"])
def Characters():
    #function to find the most common item in a list
    def most_popular(lis):
        names = {}
        most = -1
        name = ""

        for item in lis:
            if item in names:
                names[item] += 1
            else:
                names[item] = 1
    
        for key in names:
            if names[key] > most:
                most = names[key]
                name = key
    
        return name

    form = CharacterForm()
    db = get_db()
    characters = db.execute("""SELECT * FROM characters""").fetchall()


    speciesPop = []
    levelMean = 0
    classNamePop = []


    for items in characters:
        speciesPop.append(items["species"])
        levelMean += items["level"]
        classNamePop.append(items["class"])
    
    levelMean = round(levelMean/len(characters),1)
    speciesPop = most_popular(speciesPop)
    classNamePop = most_popular(classNamePop)


    if form.validate_on_submit():
        #collecting the data from the search bars and loading them into dictionary corisponding to
        #the database columns
        search = {"name": form.CharName.data, "species" : form.species.data, "level" : form.level.data, "class": form.className.data, "user_id": form.user_id.data}
        query = "SELECT * FROM characters WHERE 1=1"
        terms = []

        #building up the query depending on which fields are filled in
        for column in search:
            if search[column] != None and search[column] != "":
                query += f" AND {column} LIKE ?"
                terms.append(f"%{search[column]}%")
                                                  
        characters = db.execute(query,tuple(terms)).fetchall()
    

    return render_template("characters.html", characters = characters, form = form, levelMean = levelMean, speciesPop = speciesPop, classNamePop = classNamePop)

@app.route("/Create_campaign", methods=["GET", "POST"])
@login_required
def Create_campaign():
    form = Create_campaignForm()
    db = get_db()
    friend_reqs = db.execute("""SELECT * FROM friends 
                              WHERE (friend_id = ? AND accepted = 1) 
                              OR (user_id = ? AND accepted = 1)""",(session["user_id"],session["user_id"])).fetchall()

    for req in friend_reqs:
        if req["user_id"] != session["user_id"]:
            form.players.choices.append((req["user_id"],req["user_id"]))
        if req["friend_id"] != session["user_id"]:
            form.players.choices.append((req["friend_id"],req["friend_id"]))


    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        players = form.players.data

        db.execute("""INSERT INTO campaigns (dm_id, name, description)
                              VALUES (?, ?, ?);""", (session["user_id"],name,description))
        db.commit()
        campaign_id = db.execute("""SELECT * FROM campaigns 
                                 WHERE dm_id = ? AND name = ? AND description = ?""", (session["user_id"],name,description)).fetchone()
        

        for player in players:
            db.execute("""INSERT INTO in_campaign (user_id, campaign_id)
                              VALUES (?, ?);""", (player,campaign_id["campaign_id"]))
            db.commit()
        
        return redirect(url_for("Campaigns"))


    return render_template("campaign_create_form.html", 
                           form=form)

@app.route("/Campaigns", methods=["GET", "POST"])
def Campaigns():

    db = get_db()
    campaigns = db.execute("""SELECT * FROM campaigns""").fetchall()
    players = db.execute("""SELECT * FROM in_campaign""").fetchall()

    return render_template("campaigns.html", campaigns = campaigns, players = players)


@app.route("/user/<user_id>", methods=["GET", "POST"])
@login_required
def user(user_id):
    form = FriendForm()
    db = get_db()
    user_data = db.execute("""SELECT * FROM users WHERE user_id = ?""",(user_id,)).fetchone()
    characters = db.execute("""SELECT * FROM characters WHERE user_id = ?""", (user_id,)).fetchall()
    in_campaigns = db.execute("""SELECT * FROM campaigns
                               WHERE campaign_id in (
                               SELECT campaign_id FROM in_campaign 
                               WHERE user_id = ?)""", (user_id,)).fetchall()
    
    running = db.execute("""SELECT * FROM campaigns
                               WHERE dm_id = ?""", (user_id,)).fetchall()
    print(running)

    outgoing = []
    incoming = []
    friends = []

    #for other users
    if session["user_id"] != user_id:

        friend = db.execute("""SELECT * FROM friends 
                              WHERE (user_id = ? AND friend_id = ?) 
                              OR (friend_id = ? AND user_id = ?)""",(session["user_id"],user_id,session["user_id"],user_id)).fetchone()
        

        print(friend)
        if form.validate_on_submit():
            if friend is None:
                db.execute("""INSERT INTO friends (user_id, friend_id)
                                  VALUES (?, ?);""", (session["user_id"],user_id))
                db.commit()
            elif friend["user_id"] != session["user_id"] and friend["accepted"] != 1:
                db.execute("""UPDATE friends
                           SET accepted = 1
                           WHERE (user_id = ? AND friend_id = ?) 
                           OR (friend_id = ? AND user_id = ?)""",(session["user_id"],user_id,session["user_id"],user_id))
                db.commit()
            elif friend["accepted"] == 1:
                form.submit.errors.append("You are friends!")
            else:
                form.submit.errors.append("You have already sent a friend request")

    #for your account
    else:
        requests = db.execute("""SELECT * FROM friends 
                              WHERE user_id = ? OR friend_id = ?""",(session["user_id"],session["user_id"])).fetchall()
        
        if len(requests) != 0:
            for request in requests:
                if request["user_id"] == user_id and request["accepted"] == 0:
                    outgoing.append(request["friend_id"])
                elif request["user_id"] != user_id and request["accepted"] == 0:
                    incoming.append(request["user_id"])
                elif request["user_id"] == user_id and request["accepted"] == 1:
                    friends.append(request["friend_id"])
                elif request["user_id"] != user_id and request["accepted"] == 1:
                    friends.append(request["user_id"])

    return render_template("user.html", characters = characters, user_data = user_data, form = form, 
                           friends = friends, outgoing = outgoing,
                             incoming = incoming, in_campaigns = in_campaigns, running = running)

@app.route("/delete_character/<int:character_id>", methods=["GET", "POST"])
def delete_character(character_id):

    db = get_db()
    validator = db.execute("""SELECT * 
               FROM characters
               WHERE user_id = ? AND character_id = ?""",(session["user_id"],character_id)).fetchone()
    if validator is not None:
        db.execute("""DELETE 
               FROM characters
               WHERE character_id = ?""",(character_id,))
        db.commit()
    return redirect(url_for("user", user_id = session["user_id"]))

@app.route("/delete_campaign/<int:campaign_id>", methods=["GET", "POST"])
def delete_campaign(campaign_id):

    db = get_db()
    validator = db.execute("""SELECT * 
               FROM campaigns
               WHERE dm_id = ? AND campaign_id = ?""",(session["user_id"],campaign_id)).fetchone()
    if validator is not None:
    
        db.execute("""DELETE 
               FROM campaigns
               WHERE campaign_id = ?;""",(campaign_id,))
        db.execute("""DELETE 
               FROM in_campaign
               WHERE campaign_id = ?;""",(campaign_id,))
        db.commit()

    return redirect(url_for("user", user_id=session["user_id"]))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


            
