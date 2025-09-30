from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
import json

class QuestionnaireForm(FlaskForm):
    """Form for creating/editing questionnaires"""
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)], 
                       render_kw={"class": "form-control", "placeholder": "Enter questionnaire title"})
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)], 
                               render_kw={"class": "form-control", "rows": "4", 
                                         "placeholder": "Enter description (optional)"})
    is_active = BooleanField('Active', render_kw={"class": "form-check-input"}, default=True)
    allow_anonymous = BooleanField('Allow Anonymous Responses', 
                                  render_kw={"class": "form-check-input"}, default=False)
    multiple_submissions = BooleanField('Allow Multiple Submissions per User', 
                                      render_kw={"class": "form-check-input"}, default=False)
    submit = SubmitField('Save Questionnaire', render_kw={"class": "btn btn-primary"})

class QuestionForm(FlaskForm):
    """Form for individual questions"""
    question_text = TextAreaField('Question', validators=[DataRequired(), Length(min=5, max=500)], 
                                 render_kw={"class": "form-control", "rows": "3", 
                                           "placeholder": "Enter your question"})
    question_type = SelectField('Question Type', 
                               choices=[
                                   ('single_choice', 'Single Choice'),
                                   ('multiple_choice', 'Multiple Choice'),
                                   ('open_ended', 'Open-ended Text'),
                                   ('scale', 'Scale (1-5)')
                               ],
                               validators=[DataRequired()], 
                               render_kw={"class": "form-select"})
    is_required = BooleanField('Required', render_kw={"class": "form-check-input"}, default=True)
    order = IntegerField('Order', validators=[NumberRange(min=0)], 
                        render_kw={"class": "form-control"}, default=0)
    
    # For choice questions - will be handled dynamically in JavaScript
    option1 = StringField('Option 1', render_kw={"class": "form-control choice-option"})
    option2 = StringField('Option 2', render_kw={"class": "form-control choice-option"})
    option3 = StringField('Option 3', render_kw={"class": "form-control choice-option"})
    option4 = StringField('Option 4', render_kw={"class": "form-control choice-option"})
    option5 = StringField('Option 5', render_kw={"class": "form-control choice-option"})

class ResponseForm(FlaskForm):
    """Base form for questionnaire responses"""
    submit = SubmitField('Submit Response', render_kw={"class": "btn btn-success"})

class SearchForm(FlaskForm):
    """Search form for questionnaires"""
    search = StringField('Search', render_kw={
        "class": "form-control", 
        "placeholder": "Search questionnaires...",
        "autocomplete": "off"
    })
    filter_by = SelectField('Filter by', choices=[
        ('all', 'All Questionnaires'),
        ('active', 'Active Only'),
        ('inactive', 'Inactive Only'),
        ('my_questionnaires', 'My Questionnaires')
    ], render_kw={"class": "form-select"})
    submit = SubmitField('Search', render_kw={"class": "btn btn-outline-primary"})

class BulkActionForm(FlaskForm):
    """Form for bulk actions on questionnaires"""
    action = SelectField('Action', choices=[
        ('', 'Select Action'),
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('delete', 'Delete')
    ], validators=[DataRequired()], render_kw={"class": "form-select"})
    submit = SubmitField('Apply', render_kw={"class": "btn btn-warning"})