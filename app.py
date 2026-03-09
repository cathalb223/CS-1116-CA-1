from flask import Flask, render_template, session, redirect, url_for, g, request
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm, CreateForm, CharacterForm
from functools import wraps

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
    def wrapped_view(*args):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args)
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
    form = CharacterForm()
    db = get_db()
    characters = db.execute("""SELECT * FROM characters""").fetchall()

    if form.validate_on_submit():
        search = {"name": form.CharName.data, "species" : form.species.data, "level" : form.level.data, "class": form.className.data, "user_id": form.user_id.data}
        query = "SELECT * FROM characters WHERE 1=1"
        terms = []
        for column in search:
            if search[column] == None or search[column] == "":
                query += f" AND ? IS NOT NULL"
                terms.append(column)
            else:
                query += f" AND {column} = ?"
                terms.append(search[column])



        print(query)
                                                  
        characters = db.execute(query,tuple(terms)).fetchall()
    return render_template("characters.html", characters = characters, form = form)





@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))