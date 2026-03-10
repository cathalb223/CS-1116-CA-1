from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, EqualTo, NumberRange, Optional


class RegistrationForm(FlaskForm):
    user_id = StringField("User ID: ", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField("User ID: ", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class CreateForm(FlaskForm):
    CharName = StringField("Character Name: ", validators=[InputRequired()])
    species = SelectField("Species: ",choices=["Human","Dwarf","Elf","Tiefling","Halfling","Orc"], validators=[InputRequired()])
    level = IntegerField("Level: ", validators=[InputRequired(),NumberRange(1,20)])
    className = SelectField("Class: ", choices=["Wizard", "Druid", "Cleric", "Fighter", "Paladin", "Sorcerer", "Warlock","Ranger","Monk","Rogue", "Barbarian"], validators=[InputRequired()])
    submit = SubmitField("Submit")

class CharacterForm(FlaskForm):
    CharName = StringField("Character Name: ")
    species = SelectField("Species: ",choices=["","Human","Dwarf","Elf","Tiefling","Halfling","Orc"])
    level = IntegerField("Level:", validators = [Optional()])
    className = SelectField("Class: ", choices=["", "Wizard", "Druid", "Cleric", "Fighter", "Paladin", "Sorcerer", "Warlock","Ranger","Monk","Rogue", "Barbarian"])
    user_id = StringField("User_id: ")
    submit = SubmitField("Submit")