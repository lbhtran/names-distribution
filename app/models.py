from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

names_assignment = db.Table('names_assignment',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('name_id', db.Integer, db.ForeignKey('refugee.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    names_assigned = db.relationship(
        'Refugee', secondary=names_assignment,
        backref=db.backref('names_assignments', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

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
        if not self.is_assigned(user):
            self.names_assignments.append(user)

    def is_assigned(self, user):
        return self.names_assignments.filter(
            names_assignment.user_id == user.id).count() > 0

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

