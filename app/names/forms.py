from flask_wtf import FlaskForm
from flask import request
from wtforms import FileField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class UploadCSVForm(FlaskForm):
    fileName = FileField()
    submit = SubmitField(_l('Upload'))