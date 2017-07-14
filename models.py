from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = False
app.secret_key = 'dillybar'
db = SQLAlchemy(app)


class Blog(db.Model):
    '''Blog model that creates each blog post takes in title, body, pub_date'''

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(12000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, pub_date=None):
        '''Initial parameters for the Blog class'''
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.owner = owner

class User(db.Model):
    '''User model that creates each unique user with an id, username, password and also
     keeps a relationship to the Blog class'''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    pw_hash = db.Column(db.String(256))
    blogs = db.relationship('Blog', backref='owner')  

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


def validate_user(username, password, verify):
    '''Validate username and password entered. Return specified failure if failed'''
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        flash('That username is already in use, choose another', 'error')
        return 'error'
   
    if not username or not password or not verify:
        flash('One or more fields are invalid', 'error')
        return 'error'

    if len(username) < 3 or len(username) > 20 or re.search(r'\s', username):
        flash('Not a valid username, please enter a username without spaces at least 3 characters long but no longer than 20', 'error')
        return 'error'

    if len(password) >= 3 and len(password) <= 20:
        if re.search(r'\s', password):
            flash('Not a valid password, please enter a password between 3 and 20 characters long', 'error') 
            return 'error'
    else:
        flash('Not a valid password, please enter a password between 3 and 20 characters long', 'error')
        return 'error'
    
    if verify != password:
        flash('Your passwords did not match', 'error')
        return 'error'
