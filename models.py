from main import db, app
from datetime import datetime


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
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')   
