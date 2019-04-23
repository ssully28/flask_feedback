from flask import Flask, request, render_template, redirect, flash, session
from forms import RegisterForm, LoginForm, AddFeedback
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from flask_bcrypt import Bcrypt

# If using DB:
# from models import db, connect_db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = "super-secret-key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-feedback'
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

    if "user_id" in session:
        username = session["user_id"]
        return redirect(f'/users/{username}')

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            flash("Username already taken")
            form = RegisterForm(obj=user)
            return render_template('register.html', form=form)

        session["user_id"] = user.username
        
        return redirect(f'/users/{username}')
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
    user = User.query.get_or_404(username)
    # check that user is authenticated...
    if session["user_id"] != user.username:
        flash("Please log in to see this page")
        return redirect("/")
    else:

        return render_template('user.html', user=user)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):

    try:
        user = User.query.get_or_404(username)
        if session["user_id"] == user.username:
            # show the edit form
            db.session.delete(user)
            db.session.commit()
            session.pop("user_id")

            return redirect("/")
            
        else:
            flash("Please log in to see this page")
            
            return redirect("/")

    except KeyError:
        flash("Please log in to see this page")
        return redirect("/")


@app.route("/logout")
def logout():
    session.pop("user_id")
    return redirect("/")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):

    try:
        if session["user_id"] == username:
            # show the edit form
            form = AddFeedback()

            if form.validate_on_submit():
                title = form.title.data
                content = form.content.data

                feedback = Feedback(title=title, content=content,
                                    username=username)

                db.session.add(feedback)
                db.session.commit()

                return redirect(f"/users/{username}")

            else:
                return render_template("add-feedback.html", form=form)

        else:
            flash("Please log in to see this page")
            
            return redirect("/")

    except KeyError:
        flash("Please log in to see this page")
        return redirect("/")


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):

    try:
        feedback = Feedback.query.get(feedback_id)
        if session["user_id"] == feedback.username:
            # show the edit form
            form = AddFeedback(obj=feedback)

            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data

                db.session.add(feedback)
                db.session.commit()

                return redirect(f"/users/{feedback.username}")

            else:
                return render_template("edit-feedback.html", form=form)

        else:
            flash("Please log in to see this page")
            
            return redirect("/")

    except KeyError:
        flash("Please log in to see this page")
        return redirect("/")


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    
    try:
        feedback = Feedback.query.get(feedback_id)
        if session["user_id"] == feedback.username:
            # show the edit form
            db.session.delete(feedback)
            db.session.commit()

            return redirect(f"/users/{feedback.username}")

        else:
            flash("Please log in to see this page")
            
            return redirect("/")

    except KeyError:
        flash("Please log in to see this page")
        return redirect("/")