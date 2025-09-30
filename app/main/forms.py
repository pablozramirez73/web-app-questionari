from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Optional, ValidationError

class ChoiceForm(FlaskForm):
    text = StringField('Choice Text', validators=[Optional()])

class QuestionForm(FlaskForm):
    text = StringField('Question Text', validators=[DataRequired()])
    question_type = SelectField('Question Type', choices=[
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('open_ended', 'Open-Ended'),
        ('scale', 'Scale (1-5)')
    ], validators=[DataRequired()])
    choices = FieldList(FormField(ChoiceForm), min_entries=0)

    def validate_choices(self, field):
        if self.question_type.data in ['single_choice', 'multiple_choice']:
            if not any(c.data['text'] for c in field.entries):
                 raise ValidationError('At least one choice is required for this question type.')
            for entry in field.entries:
                if not entry.data['text']:
                    raise ValidationError('Choice text cannot be empty for this question type.')

class QuestionnaireForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    questions = FieldList(FormField(QuestionForm), min_entries=1)
    submit = SubmitField('Create Questionnaire')