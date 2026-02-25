from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, PasswordField
from wtforms.validators import InputRequired, EqualTo


class RegistrationForm(FlaskForm):
    user_id = StringField("Band:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Password:", validators=[InputRequired(),EqualTo("password")])
    submit = SubmitField("Submit")