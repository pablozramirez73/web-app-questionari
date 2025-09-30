from datetime import datetime
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default='user')  # user, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    created_questionnaires = db.relationship('Questionnaire', foreign_keys='Questionnaire.creator_id', 
                                           backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    responses = db.relationship('Response', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Questionnaire(db.Model):
    """Questionnaire model"""
    __tablename__ = 'questionnaires'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    allow_anonymous = db.Column(db.Boolean, default=False)
    multiple_submissions = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='questionnaire', lazy='dynamic', 
                              cascade='all, delete-orphan', order_by='Question.order')
    responses = db.relationship('Response', backref='questionnaire', lazy='dynamic', 
                              cascade='all, delete-orphan')
    
    def get_total_responses(self):
        """Get total number of responses"""
        return self.responses.filter_by(is_complete=True).count()
    
    def get_completion_rate(self):
        """Get completion rate percentage"""
        total = self.responses.count()
        completed = self.responses.filter_by(is_complete=True).count()
        return (completed / total * 100) if total > 0 else 0
    
    def get_question_count(self):
        """Get total number of questions"""
        return self.questions.count()
    
    def can_user_respond(self, user):
        """Check if user can respond to questionnaire"""
        if not self.is_active:
            return False, "Questionnaire is not active"
        
        if not self.multiple_submissions and user:
            existing = Response.query.filter_by(
                questionnaire_id=self.id,
                user_id=user.id,
                is_complete=True
            ).first()
            if existing:
                return False, "You have already completed this questionnaire"
        
        return True, "Can respond"
    
    def __repr__(self):
        return f'<Questionnaire {self.title}>'

class Question(db.Model):
    """Question model"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # single_choice, multiple_choice, open_ended, scale
    options = db.Column(db.Text)  # JSON string for choice options
    order = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_options_list(self):
        """Get options as list"""
        if self.options:
            try:
                return json.loads(self.options)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_options_list(self, options_list):
        """Set options from list"""
        self.options = json.dumps(options_list) if options_list else None
    
    def get_answer_statistics(self):
        """Get statistics for question answers"""
        if self.question_type in ['single_choice', 'multiple_choice']:
            stats = {}
            options = self.get_options_list()
            
            for option in options:
                count = self.answers.filter(
                    Answer.answer_value.contains(option)
                ).count()
                stats[option] = count
            
            return stats
        
        elif self.question_type == 'scale':
            stats = {}
            for i in range(1, 6):
                count = self.answers.filter_by(answer_value=str(i)).count()
                stats[str(i)] = count
            return stats
        
        return {}
    
    def __repr__(self):
        return f'<Question {self.question_text[:50]}...>'

class Response(db.Model):
    """Response model - represents a user's response to a questionnaire"""
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous
    session_id = db.Column(db.String(255))  # For anonymous users
    is_complete = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='response', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_progress_percentage(self):
        """Get completion progress percentage"""
        total_questions = self.questionnaire.questions.filter_by(is_required=True).count()
        answered_questions = self.answers.join(Question).filter(Question.is_required == True).count()
        return (answered_questions / total_questions * 100) if total_questions > 0 else 0
    
    def get_respondent_name(self):
        """Get respondent name (user or anonymous)"""
        if self.user:
            return self.user.get_full_name()
        return f"Anonymous ({self.session_id[:8]}...)" if self.session_id else "Anonymous"
    
    def __repr__(self):
        return f'<Response {self.id} for Questionnaire {self.questionnaire_id}>'

class Answer(db.Model):
    """Answer model - represents an answer to a specific question"""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_value = db.Column(db.Text)  # For choice questions (JSON array for multiple choice)
    answer_text = db.Column(db.Text)   # For open-ended questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_value_list(self):
        """Get answer value as list (for multiple choice)"""
        if self.answer_value:
            try:
                return json.loads(self.answer_value)
            except json.JSONDecodeError:
                return [self.answer_value]
        return []
    
    def set_value_list(self, values):
        """Set answer value from list"""
        if isinstance(values, list):
            self.answer_value = json.dumps(values)
        else:
            self.answer_value = str(values)
    
    def get_display_value(self):
        """Get formatted display value"""
        if self.question.question_type == 'open_ended':
            return self.answer_text or 'No answer'
        elif self.question.question_type in ['single_choice', 'multiple_choice']:
            values = self.get_value_list()
            return ', '.join(values) if values else 'No answer'
        elif self.question.question_type == 'scale':
            return f"{self.answer_value}/5" if self.answer_value else 'No answer'
        return self.answer_value or 'No answer'
    
    def __repr__(self):
        return f'<Answer {self.id} for Question {self.question_id}>'