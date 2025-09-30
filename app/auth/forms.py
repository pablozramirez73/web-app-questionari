from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username or Email', validators=[DataRequired()], 
                          render_kw={"class": "form-control", "placeholder": "Enter username or email"})
    password = PasswordField('Password', validators=[DataRequired()], 
                           render_kw={"class": "form-control", "placeholder": "Enter password"})
    remember_me = BooleanField('Remember Me', render_kw={"class": "form-check-input"})
    submit = SubmitField('Sign In', render_kw={"class": "btn btn-primary w-100"})

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)], 
                          render_kw={"class": "form-control", "placeholder": "Choose a username"})
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       render_kw={"class": "form-control", "placeholder": "Enter email address"})
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)], 
                            render_kw={"class": "form-control", "placeholder": "Enter first name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)], 
                           render_kw={"class": "form-control", "placeholder": "Enter last name"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], 
                           render_kw={"class": "form-control", "placeholder": "Choose a password"})
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')], 
        render_kw={"class": "form-control", "placeholder": "Confirm password"})
    submit = SubmitField('Register', render_kw={"class": "btn btn-success w-100"})
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address already registered. Please use a different one.')

class EditProfileForm(FlaskForm):
    """Edit user profile form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)], 
                          render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], 
                       render_kw={"class": "form-control"})
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)], 
                            render_kw={"class": "form-control"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)], 
                           render_kw={"class": "form-control"})
    submit = SubmitField('Update Profile', render_kw={"class": "btn btn-primary"})
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Email address already registered. Please use a different one.')

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[DataRequired()], 
                                   render_kw={"class": "form-control", "placeholder": "Enter current password"})
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)], 
                           render_kw={"class": "form-control", "placeholder": "Enter new password"})
    password2 = PasswordField('Repeat New Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')], 
        render_kw={"class": "form-control", "placeholder": "Confirm new password"})
    submit = SubmitField('Change Password', render_kw={"class": "btn btn-warning"})