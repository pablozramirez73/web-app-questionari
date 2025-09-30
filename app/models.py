from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    questionnaires = db.relationship('Questionnaire', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('Question', backref='questionnaire', lazy='dynamic')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(280))
    question_type = db.Column(db.String(20))  # single_choice, multiple_choice, open_ended, scale
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaire.id'))
    choices = db.relationship('Choice', backref='question', lazy='dynamic')

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    choice_id = db.Column(db.Integer, db.ForeignKey('choice.id'))
    text = db.Column(db.Text)
    scale_value = db.Column(db.Integer)
    user = db.relationship('User', backref='answers')
    question = db.relationship('Question', backref='answers')
    choice = db.relationship('Choice', backref='answers')