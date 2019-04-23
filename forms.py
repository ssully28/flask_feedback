from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    """Form for registration"""

    username = StringField("Username",
                           validators=[InputRequired(), Length(min=4, max=20)])

    password = PasswordField("Password", validators=[InputRequired(), 
                             Length(min=8, max=20)])

    email = StringField("Email",
                        validators=[InputRequired(), Length(max=50), Email()])

    first_name = StringField("First Name", validators=[InputRequired(),
                            Length(max=30)])

    last_name = StringField("Last Name", validators=[InputRequired(),
                           Length(max=30)])


class LoginForm(FlaskForm):
    """Form for login"""

    username = StringField("Username", validators=[InputRequired(),
                           Length(min=4, max=20)])

    password = PasswordField("Password", validators=[InputRequired(),
                             Length(min=8, max=20)])