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