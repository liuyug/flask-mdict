from flask_wtf import FlaskForm
from wtforms import StringField


class WordForm(FlaskForm):
    word = StringField('Word')
