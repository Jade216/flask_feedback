
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    '''connect this database to Flask app'''
    db.app = app
    db.init_app(app)


class User(db.Model):
    '''site user'''
    __tablename__ = 'users'

    username = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    feedback = db.relationship('Feedback', backref='user')

    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        '''register a user and hashing the password'''
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf-8')
        user = cls(
            username = username,
            password = hashed_utf8,
            first_name = first_name,
            last_name = last_name,
            email = email
        )
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        '''validate that user exists & password is correct'''
        user =  cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    @property
    def full_name(self):
        '''Return the full name of the user.'''
        return f"{self.first_name} {self.last_name}"



class Feedback(db.Model):
    '''feedback'''
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)


