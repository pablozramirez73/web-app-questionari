from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc, or_
from app import db
from app.main import bp
from app.main.forms import QuestionnaireForm, QuestionForm, SearchForm
from app.models import User, Questionnaire, Question, Response, Answer
import json

@bp.route('/')
def index():
    """Home page"""
    # Get some basic statistics for public display
    total_questionnaires = Questionnaire.query.filter_by(is_active=True).count()
    total_responses = Response.query.filter_by(is_complete=True).count()
    
    return render_template('main/index.html', 
                         title='Home',
                         total_questionnaires=total_questionnaires,
                         total_responses=total_responses)

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's questionnaires
    user_questionnaires = current_user.created_questionnaires.order_by(desc(Questionnaire.created_at)).limit(5).all()
    
    # Get user's recent responses
    user_responses = current_user.responses.order_by(desc(Response.submitted_at)).limit(5).all()
    
    # Get statistics
    stats = {
        'total_questionnaires': current_user.created_questionnaires.count(),
        'active_questionnaires': current_user.created_questionnaires.filter_by(is_active=True).count(),
        'total_responses_received': db.session.query(Response).join(Questionnaire).filter(
            Questionnaire.creator_id == current_user.id,
            Response.is_complete == True
        ).count(),
        'my_responses': current_user.responses.filter_by(is_complete=True).count()
    }
    
    return render_template('main/dashboard.html', 
                         title='Dashboard',
                         user_questionnaires=user_questionnaires,
                         user_responses=user_responses,
                         stats=stats)

@bp.route('/questionnaires')
def questionnaires():
    """List all active questionnaires"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    filter_by = request.args.get('filter_by', 'all', type=str)
    
    # Base query
    query = Questionnaire.query
    
    # Apply filters
    if filter_by == 'active':
        query = query.filter_by(is_active=True)
    elif filter_by == 'inactive':
        query = query.filter_by(is_active=False)
    elif filter_by == 'my_questionnaires' and current_user.is_authenticated:
        query = query.filter_by(creator_id=current_user.id)
    
    # Apply search
    if search:
        query = query.filter(or_(
            Questionnaire.title.contains(search),
            Questionnaire.description.contains(search)
        ))
    
    # If not logged in, show only active questionnaires
    if not current_user.is_authenticated:
        query = query.filter_by(is_active=True)
    
    questionnaires = query.order_by(desc(Questionnaire.created_at)).paginate(
        page=page, 
        per_page=current_app.config['QUESTIONNAIRES_PER_PAGE'],
        error_out=False
    )
    
    search_form = SearchForm()
    search_form.search.data = search
    search_form.filter_by.data = filter_by
    
    return render_template('main/questionnaires.html',
                         title='Questionnaires',
                         questionnaires=questionnaires,
                         search_form=search_form)

@bp.route('/questionnaire/<int:id>')
def view_questionnaire(id):
    """View questionnaire details"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check if user can view this questionnaire
    if not questionnaire.is_active and questionnaire.creator != current_user and not current_user.is_authenticated:
        flash('This questionnaire is not available.', 'warning')
        return redirect(url_for('main.questionnaires'))
    
    # Check if user has already responded
    user_response = None
    if current_user.is_authenticated:
        user_response = Response.query.filter_by(
            questionnaire_id=id,
            user_id=current_user.id,
            is_complete=True
        ).first()
    
    can_respond, message = questionnaire.can_user_respond(current_user if current_user.is_authenticated else None)
    
    return render_template('main/view_questionnaire.html',
                         title=questionnaire.title,
                         questionnaire=questionnaire,
                         user_response=user_response,
                         can_respond=can_respond,
                         response_message=message)

@bp.route('/create-questionnaire', methods=['GET', 'POST'])
@login_required
def create_questionnaire():
    """Create new questionnaire"""
    form = QuestionnaireForm()
    if form.validate_on_submit():
        questionnaire = Questionnaire(
            title=form.title.data,
            description=form.description.data,
            creator_id=current_user.id,
            is_active=form.is_active.data,
            allow_anonymous=form.allow_anonymous.data,
            multiple_submissions=form.multiple_submissions.data
        )
        db.session.add(questionnaire)
        db.session.commit()
        
        flash('Questionnaire created successfully! Now add some questions.', 'success')
        return redirect(url_for('main.edit_questionnaire', id=questionnaire.id))
    
    return render_template('main/create_questionnaire.html', 
                         title='Create Questionnaire', 
                         form=form)

@bp.route('/edit-questionnaire/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_questionnaire(id):
    """Edit questionnaire and its questions"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check permissions
    if questionnaire.creator != current_user and not current_user.is_admin():
        flash('You do not have permission to edit this questionnaire.', 'danger')
        return redirect(url_for('main.questionnaires'))
    
    form = QuestionnaireForm()
    if form.validate_on_submit():
        questionnaire.title = form.title.data
        questionnaire.description = form.description.data
        questionnaire.is_active = form.is_active.data
        questionnaire.allow_anonymous = form.allow_anonymous.data
        questionnaire.multiple_submissions = form.multiple_submissions.data
        db.session.commit()
        
        flash('Questionnaire updated successfully!', 'success')
        return redirect(url_for('main.edit_questionnaire', id=questionnaire.id))
    
    elif request.method == 'GET':
        form.title.data = questionnaire.title
        form.description.data = questionnaire.description
        form.is_active.data = questionnaire.is_active
        form.allow_anonymous.data = questionnaire.allow_anonymous
        form.multiple_submissions.data = questionnaire.multiple_submissions
    
    # Get questions ordered by their order field
    questions = questionnaire.questions.order_by(Question.order).all()
    
    return render_template('main/edit_questionnaire.html',
                         title='Edit Questionnaire',
                         form=form,
                         questionnaire=questionnaire,
                         questions=questions)

@bp.route('/questionnaire/<int:id>/delete', methods=['POST'])
@login_required
def delete_questionnaire(id):
    """Delete questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check permissions
    if questionnaire.creator != current_user and not current_user.is_admin():
        flash('You do not have permission to delete this questionnaire.', 'danger')
        return redirect(url_for('main.questionnaires'))
    
    db.session.delete(questionnaire)
    db.session.commit()
    
    flash('Questionnaire deleted successfully.', 'success')
    return redirect(url_for('main.questionnaires'))

@bp.route('/my-questionnaires')
@login_required
def my_questionnaires():
    """List user's questionnaires"""
    page = request.args.get('page', 1, type=int)
    questionnaires = current_user.created_questionnaires.order_by(
        desc(Questionnaire.created_at)
    ).paginate(
        page=page, 
        per_page=current_app.config['QUESTIONNAIRES_PER_PAGE'],
        error_out=False
    )
    
    return render_template('main/my_questionnaires.html',
                         title='My Questionnaires',
                         questionnaires=questionnaires)

@bp.route('/questionnaire/<int:id>/analytics')
@login_required
def questionnaire_analytics(id):
    """View questionnaire analytics and charts"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check permissions
    if questionnaire.creator != current_user and not current_user.is_admin():
        flash('You do not have permission to view analytics for this questionnaire.', 'danger')
        return redirect(url_for('main.questionnaires'))
    
    # Get basic statistics
    total_responses = questionnaire.responses.filter_by(is_complete=True).count()
    total_started = questionnaire.responses.count()
    completion_rate = (total_responses / total_started * 100) if total_started > 0 else 0
    
    # Get response timeline data (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    timeline_data = db.session.query(
        func.date(Response.submitted_at).label('date'),
        func.count(Response.id).label('count')
    ).filter(
        Response.questionnaire_id == id,
        Response.is_complete == True,
        Response.submitted_at >= thirty_days_ago
    ).group_by(func.date(Response.submitted_at)).all()
    
    # Generate enhanced charts using the new utilities
    from app.utils import ChartGenerator
    
    timeline_chart = ChartGenerator.generate_response_timeline_chart(questionnaire)
    completion_chart = ChartGenerator.generate_completion_rate_chart(questionnaire)
    user_response_chart = ChartGenerator.generate_user_response_chart(questionnaire)
    
    # Get question analytics with charts
    questions_data = []
    for question in questionnaire.questions.order_by(Question.order):
        stats = question.get_answer_statistics()
        question_chart = ChartGenerator.generate_question_chart(question)
        
        questions_data.append({
            'id': question.id,
            'text': question.question_text,
            'type': question.question_type,
            'stats': stats,
            'chart': question_chart,
            'total_answers': sum(stats.values()) if stats else 0,
            'response_rate': (sum(stats.values()) / total_responses * 100) if total_responses > 0 else 0
        })
    
    # Get respondent demographics (if available)
    user_responses = questionnaire.responses.filter_by(is_complete=True).filter(Response.user_id.isnot(None)).count()
    anonymous_responses = questionnaire.responses.filter_by(is_complete=True).filter(Response.user_id.is_(None)).count()
    
    # Calculate additional analytics
    average_completion_time = calculate_average_completion_time(questionnaire)
    peak_response_hours = get_peak_response_hours(questionnaire)
    
    return render_template('main/questionnaire_analytics.html',
                         title=f'Analytics - {questionnaire.title}',
                         questionnaire=questionnaire,
                         total_responses=total_responses,
                         total_started=total_started,
                         completion_rate=completion_rate,
                         timeline_data=timeline_data,
                         timeline_chart=timeline_chart,
                         completion_chart=completion_chart,
                         user_response_chart=user_response_chart,
                         questions_data=questions_data,
                         user_responses=user_responses,
                         anonymous_responses=anonymous_responses,
                         average_completion_time=average_completion_time,
                         peak_response_hours=peak_response_hours)

def calculate_average_completion_time(questionnaire):
    """Calculate average time to complete questionnaire"""
    from app.models import Response
    
    completed_responses = questionnaire.responses.filter_by(is_complete=True).all()
    if not completed_responses:
        return None
    
    # For now, return a placeholder - in real implementation, you'd track start/end times
    return "5-10 minutes (estimated)"

def get_peak_response_hours(questionnaire):
    """Get peak hours for responses"""
    from app.models import Response
    from sqlalchemy import func
    
    hourly_data = db.session.query(
        func.extract('hour', Response.submitted_at).label('hour'),
        func.count(Response.id).label('count')
    ).filter(
        Response.questionnaire_id == questionnaire.id,
        Response.is_complete == True
    ).group_by(func.extract('hour', Response.submitted_at)).all()
    
    if hourly_data:
        peak_hour = max(hourly_data, key=lambda x: x.count)
        return f"{int(peak_hour.hour):02d}:00 - {int(peak_hour.hour)+1:02d}:00"
    
    return "No data available"

@bp.route('/questionnaire/<int:id>/responses')
@login_required
def questionnaire_responses(id):
    """View individual responses for a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check permissions
    if questionnaire.creator != current_user and not current_user.is_admin():
        flash('You do not have permission to view responses for this questionnaire.', 'danger')
        return redirect(url_for('main.questionnaires'))
    
    page = request.args.get('page', 1, type=int)
    responses = questionnaire.responses.filter_by(is_complete=True).order_by(
        desc(Response.submitted_at)
    ).paginate(
        page=page,
        per_page=current_app.config['RESPONSES_PER_PAGE'],
        error_out=False
    )
    
    return render_template('main/questionnaire_responses.html',
                         title=f'Responses - {questionnaire.title}',
                         questionnaire=questionnaire,
                         responses=responses)

@bp.route('/questionnaire/<int:id>/export')
@login_required
def export_questionnaire_data(id):
    """Export questionnaire data to CSV"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check permissions
    if questionnaire.creator != current_user and not current_user.is_admin():
        flash('You do not have permission to export data for this questionnaire.', 'danger')
        return redirect(url_for('main.questionnaires'))
    
    import csv
    import io
    from flask import make_response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['Response ID', 'Respondent', 'Submitted At', 'Complete']
    for question in questionnaire.questions.order_by(Question.order):
        header.append(f'Q{question.order + 1}: {question.question_text}')
    writer.writerow(header)
    
    # Write data
    for response in questionnaire.responses.filter_by(is_complete=True):
        row = [
            response.id,
            response.get_respondent_name(),
            response.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Yes' if response.is_complete else 'No'
        ]
        
        for question in questionnaire.questions.order_by(Question.order):
            answer = response.answers.filter_by(question_id=question.id).first()
            if answer:
                row.append(answer.get_display_value())
            else:
                row.append('')
        
        writer.writerow(row)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=questionnaire_{id}_responses.csv'
    
    return response