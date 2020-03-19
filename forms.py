from flask_wtf import FlaskForm
from wtforms import StringField,  PasswordField
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[
                           InputRequired(), Length(max=20)])

    password = PasswordField("Password", validators=[InputRequired()])

    email = StringField("Email", validators=[
                        Email(), InputRequired(), Length(max=50)])

    first_name = StringField("First Name", validators=[
                             InputRequired(), Length(max=30)])

    last_name = StringField("Last Name", validators=[
                            InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField("Username", validators=[
                           InputRequired(), Length(max=20)])

    password = PasswordField("Password", validators=[InputRequired()])
