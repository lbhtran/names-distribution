from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login, admin

names_assignment = db.Table('names_assignment',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('name_id', db.Integer, db.ForeignKey('refugee.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    names_assigned = db.relationship(
        'Refugee', secondary=names_assignment,
        backref=db.backref('names_assignment', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def get_assigned_list(self):
        return Refugee.query.join(
            names_assignment, (names_assignment.c.name_id == Refugee.id)).filter(
                names_assignment.c.user_id == self.id).order_by(
                    Refugee.id.asc())

class Refugee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(100), index=True)
    origin = db.Column(db.String(50))
    found = db.Column(db.Integer)
    cause_of_death = db.Column(db.String(280))
    source = db.Column(db.String(50))

    def __repr__(self):
        return '<Refugee {}>'.format(self.identity)

    def assign_name(self, user):
        if not self.is_assigned():
            self.names_assignment.append(user)

    def is_assigned(self):
        return self.names_assignment.filter(
            names_assignment.c.name_id == self.id).count() > 0

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Refugee, db.session))
