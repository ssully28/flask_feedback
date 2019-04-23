from flask import Flask, request, render_template, redirect, flash, session
from forms import RegisterForm, LoginForm
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from flask_bcrypt import Bcrypt

# If using DB:
# from models import db, connect_db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = "super-secret-key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

bcrypt = Bcrypt()

connect_db(app)
db.create_all()


@app.route("/")
def home_route():
    """Home Page Route."""
    return redirect("/register")


@app.route("/register", methods=["POST", "GET"])
def registration():

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.username
        
        return redirect('/secret')
    else:
        return render_template('register.html', form=form)


@app.route("/login", methods=["POST", "GET"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["user_id"] = user.username
            return redirect(f'/users/{username}')
        else:
            return render_template('register.html', form=form)

    else:
        return render_template('register.html', form=form)


@app.route("/users/<username>")
def user_page(username):

    # check that user is authenticated...
    if "user_id" not in session:
        flash("Please log in to see this page")
        return redirect("/")
    else:
        user = User.query.get(username)
        return render_template('user.html', user=user)

@app.route("/logout")
def logout():
    session.pop("user_id")
    return redirect("/")