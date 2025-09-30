from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.main.forms import QuestionnaireForm
from app.models import User, Questionnaire, Question, Choice, Answer

@bp.route('/')
@bp.route('/index')
def index():
    questionnaires = Questionnaire.query.all()
    return render_template('index.html', title='Home', questionnaires=questionnaires)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    questionnaires = user.questionnaires.order_by(Questionnaire.id.desc())
    return render_template('user.html', user=user, questionnaires=questionnaires)

@bp.route('/create_questionnaire', methods=['GET', 'POST'])
@login_required
def create_questionnaire():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        questionnaire = Questionnaire(title=form.title.data, description=form.description.data, author=current_user)
        db.session.add(questionnaire)
        for question_form in form.questions:
            question = Question(text=question_form.text.data, question_type=question_form.question_type.data, questionnaire=questionnaire)
            db.session.add(question)
            if question.question_type in ['single_choice', 'multiple_choice']:
                for choice_form in question_form.choices:
                    choice = Choice(text=choice_form.text.data, question=question)
                    db.session.add(choice)
        db.session.commit()
        flash('Your questionnaire has been created!')
        return redirect(url_for('main.questionnaire', questionnaire_id=questionnaire.id))
    return render_template('create_questionnaire.html', title='Create Questionnaire', form=form)

@bp.route('/questionnaire/<int:questionnaire_id>')
def questionnaire(questionnaire_id):
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    return render_template('questionnaire.html', title=questionnaire.title, questionnaire=questionnaire)

@bp.route('/questionnaire/<int:questionnaire_id>/submit', methods=['POST'])
@login_required
def submit_questionnaire(questionnaire_id):
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    for question in questionnaire.questions:
        if question.question_type == 'multiple_choice':
            choice_ids = request.form.getlist(f'question_{question.id}')
            for choice_id in choice_ids:
                answer = Answer(user_id=current_user.id, question_id=question.id, choice_id=int(choice_id))
                db.session.add(answer)
        else:
            answer = Answer(user_id=current_user.id, question_id=question.id)
            if question.question_type == 'open_ended':
                answer.text = request.form.get(f'question_{question.id}')
            elif question.question_type == 'scale':
                answer.scale_value = int(request.form.get(f'question_{question.id}'))
            elif question.question_type == 'single_choice':
                answer.choice_id = int(request.form.get(f'question_{question.id}'))
            db.session.add(answer)
    db.session.commit()
    flash('Thank you for completing the questionnaire!')
    return redirect(url_for('main.index'))

@bp.route('/questionnaire/<int:questionnaire_id>/results')
@login_required
def questionnaire_results(questionnaire_id):
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    if questionnaire.author != current_user:
        flash('You are not authorized to view the results of this questionnaire.')
        return redirect(url_for('main.index'))

    answers = Answer.query.join(Question).filter(Question.questionnaire_id == questionnaire_id).all()

    results = {}
    users = {}

    for answer in answers:
        if answer.user_id not in results:
            results[answer.user_id] = {}
            users[answer.user_id] = answer.user
        if answer.question_id not in results[answer.user_id]:
            results[answer.user_id][answer.question_id] = []

        if answer.text:
            results[answer.user_id][answer.question_id].append(answer.text)
        elif answer.scale_value:
            results[answer.user_id][answer.question_id].append(str(answer.scale_value))
        elif answer.choice:
            results[answer.user_id][answer.question_id].append(answer.choice.text)

    return render_template('questionnaire_results.html', title='Results for ' + questionnaire.title,
                           questionnaire=questionnaire, results=results, users=users)

@bp.route('/questionnaire/<int:questionnaire_id>/analysis')
@login_required
def questionnaire_analysis(questionnaire_id):
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    if questionnaire.author != current_user:
        flash('You are not authorized to analyze the results of this questionnaire.')
        return redirect(url_for('main.index'))

    charts_data = []
    for question in questionnaire.questions:
        if question.question_type in ['single_choice', 'multiple_choice', 'scale']:
            labels = []
            data = []
            if question.question_type in ['single_choice', 'multiple_choice']:
                for choice in question.choices:
                    labels.append(choice.text)
                    data.append(len(Answer.query.filter_by(choice_id=choice.id).all()))
            elif question.question_type == 'scale':
                labels = [str(i) for i in range(1, 6)]
                data = [len(Answer.query.filter_by(question_id=question.id, scale_value=i).all()) for i in range(1, 6)]

            charts_data.append({
                'question_text': question.text,
                'chart_id': f'chart_{question.id}',
                'labels': labels,
                'data': data
            })

    return render_template('questionnaire_analysis.html', title='Analysis for ' + questionnaire.title,
                           questionnaire=questionnaire, charts_data=charts_data)