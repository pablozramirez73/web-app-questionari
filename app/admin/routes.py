from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app import db
from app.admin import bp
from app.models import User, Questionnaire, Question, Response, Answer
from functools import wraps

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def admin_dashboard():
    """Admin dashboard with system statistics"""
    
    # User statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    
    # Questionnaire statistics
    total_questionnaires = Questionnaire.query.count()
    active_questionnaires = Questionnaire.query.filter_by(is_active=True).count()
    
    # Response statistics
    total_responses = Response.query.filter_by(is_complete=True).count()
    
    # Recent activity
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_questionnaires = Questionnaire.query.order_by(desc(Questionnaire.created_at)).limit(5).all()
    recent_responses = Response.query.filter_by(is_complete=True).order_by(desc(Response.submitted_at)).limit(10).all()
    
    # Monthly statistics (responses per month)
    monthly_responses = db.session.query(
        func.strftime('%Y-%m', Response.submitted_at).label('month'),
        func.count(Response.id).label('count')
    ).filter(Response.is_complete == True).group_by('month').order_by('month').limit(12).all()
    
    stats = {
        'users': {
            'total': total_users,
            'active': active_users,
            'admins': admin_users
        },
        'questionnaires': {
            'total': total_questionnaires,
            'active': active_questionnaires
        },
        'responses': {
            'total': total_responses
        }
    }
    
    return render_template('admin/dashboard.html',
                         title='Admin Dashboard',
                         stats=stats,
                         recent_users=recent_users,
                         recent_questionnaires=recent_questionnaires,
                         recent_responses=recent_responses,
                         monthly_responses=monthly_responses)

@bp.route('/users')
@admin_required
def manage_users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    users = query.order_by(desc(User.created_at)).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template('admin/users.html',
                         title='Manage Users',
                         users=users,
                         search=search)

@bp.route('/user/<int:id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(id):
    """Toggle user active status"""
    user = User.query.get_or_404(id)
    
    if user == current_user:
        flash('You cannot deactivate yourself.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_user_admin(id):
    """Toggle user admin status"""
    user = User.query.get_or_404(id)
    
    if user == current_user:
        flash('You cannot change your own admin status.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    
    role = 'promoted to admin' if user.role == 'admin' else 'removed from admin'
    flash(f'User {user.username} has been {role}.', 'success')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    """Delete user"""
    user = User.query.get_or_404(id)
    
    if user == current_user:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Check if user has questionnaires or responses
    if user.created_questionnaires.count() > 0 or user.responses.count() > 0:
        flash('Cannot delete user with existing questionnaires or responses. Deactivate instead.', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/questionnaires')
@admin_required
def manage_questionnaires():
    """Manage all questionnaires"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    filter_by = request.args.get('filter_by', 'all', type=str)
    
    query = Questionnaire.query
    
    if filter_by == 'active':
        query = query.filter_by(is_active=True)
    elif filter_by == 'inactive':
        query = query.filter_by(is_active=False)
    
    if search:
        query = query.filter(
            (Questionnaire.title.contains(search)) |
            (Questionnaire.description.contains(search))
        )
    
    questionnaires = query.order_by(desc(Questionnaire.created_at)).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    return render_template('admin/questionnaires.html',
                         title='Manage Questionnaires',
                         questionnaires=questionnaires,
                         search=search,
                         filter_by=filter_by)

@bp.route('/questionnaire/<int:id>/toggle-active', methods=['POST'])
@admin_required
def toggle_questionnaire_active(id):
    """Toggle questionnaire active status"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    questionnaire.is_active = not questionnaire.is_active
    db.session.commit()
    
    status = 'activated' if questionnaire.is_active else 'deactivated'
    flash(f'Questionnaire "{questionnaire.title}" has been {status}.', 'success')
    
    return redirect(url_for('admin.manage_questionnaires'))

@bp.route('/questionnaire/<int:id>/delete', methods=['POST'])
@admin_required
def delete_questionnaire_admin(id):
    """Delete questionnaire (admin)"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    title = questionnaire.title
    db.session.delete(questionnaire)
    db.session.commit()
    
    flash(f'Questionnaire "{title}" has been deleted.', 'success')
    return redirect(url_for('admin.manage_questionnaires'))

@bp.route('/responses')
@admin_required
def manage_responses():
    """View all responses"""
    page = request.args.get('page', 1, type=int)
    questionnaire_id = request.args.get('questionnaire_id', None, type=int)
    
    query = Response.query.filter_by(is_complete=True)
    
    if questionnaire_id:
        query = query.filter_by(questionnaire_id=questionnaire_id)
    
    responses = query.order_by(desc(Response.submitted_at)).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    # Get questionnaires for filter dropdown
    questionnaires = Questionnaire.query.order_by(Questionnaire.title).all()
    
    return render_template('admin/responses.html',
                         title='Manage Responses',
                         responses=responses,
                         questionnaires=questionnaires,
                         selected_questionnaire=questionnaire_id)

@bp.route('/statistics')
@admin_required
def system_statistics():
    """System-wide statistics and analytics"""
    
    # User growth over time
    user_growth = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count(User.id).label('count')
    ).group_by('month').order_by('month').limit(12).all()
    
    # Most active questionnaire creators
    top_creators = db.session.query(
        User,
        func.count(Questionnaire.id).label('questionnaire_count')
    ).join(Questionnaire).group_by(User.id).order_by(desc('questionnaire_count')).limit(10).all()
    
    # Most responded questionnaires
    popular_questionnaires = db.session.query(
        Questionnaire,
        func.count(Response.id).label('response_count')
    ).join(Response).filter(Response.is_complete == True).group_by(Questionnaire.id).order_by(desc('response_count')).limit(10).all()
    
     return render_template('admin/statistics.html',
                         title='System Statistics',
                         user_growth=user_growth,
                         top_creators=top_creators,
                         popular_questionnaires=popular_questionnaires)

@bp.route('/export/users-json')
@admin_required
def export_users_json():
    """Export all users to JSON format"""
    from flask import make_response
    import json
    from datetime import datetime
    
    export_data = {
        'export_info': {
            'exported_by': current_user.get_full_name(),
            'exported_at': datetime.utcnow().isoformat(),
            'export_type': 'users_only',
            'version': '1.0'
        },
        'statistics': {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'admin_users': User.query.filter_by(role='admin').count()
        },
        'users': []
    }
    
    # Export all users with detailed information
    for user in User.query.order_by('created_at'):
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'statistics': {
                'questionnaires_created': user.created_questionnaires.count(),
                'active_questionnaires': user.created_questionnaires.filter_by(is_active=True).count(),
                'responses_submitted': user.responses.filter_by(is_complete=True).count(),
                'total_responses_received': db.session.query(Response).join(Questionnaire).filter(
                    Questionnaire.creator_id == user.id,
                    Response.is_complete == True
                ).count()
            }
        }
        export_data['users'].append(user_data)
    
    # Create JSON response
    json_output = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    response = make_response(json_output)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    return response

@bp.route('/export/questionnaires-json')
@admin_required
def export_questionnaires_json():
    """Export all questionnaires to JSON format"""
    from flask import make_response
    import json
    from datetime import datetime
    
    export_data = {
        'export_info': {
            'exported_by': current_user.get_full_name(),
            'exported_at': datetime.utcnow().isoformat(),
            'export_type': 'questionnaires_only',
            'version': '1.0'
        },
        'statistics': {
            'total_questionnaires': Questionnaire.query.count(),
            'active_questionnaires': Questionnaire.query.filter_by(is_active=True).count(),
            'total_questions': Question.query.count(),
            'total_responses': Response.query.filter_by(is_complete=True).count()
        },
        'questionnaires': []
    }
    
    # Export all questionnaires with questions but without detailed responses
    for questionnaire in Questionnaire.query.order_by('created_at'):
        questionnaire_data = {
            'id': questionnaire.id,
            'title': questionnaire.title,
            'description': questionnaire.description,
            'creator': {
                'id': questionnaire.creator.id,
                'username': questionnaire.creator.username,
                'full_name': questionnaire.creator.get_full_name()
            },
            'settings': {
                'is_active': questionnaire.is_active,
                'allow_anonymous': questionnaire.allow_anonymous,
                'multiple_submissions': questionnaire.multiple_submissions
            },
            'metadata': {
                'created_at': questionnaire.created_at.isoformat(),
                'updated_at': questionnaire.updated_at.isoformat(),
                'total_questions': questionnaire.get_question_count(),
                'total_responses': questionnaire.get_total_responses(),
                'completion_rate': questionnaire.get_completion_rate()
            },
            'questions': []
        }
        
        # Export questions for this questionnaire
        for question in questionnaire.questions.order_by('order'):
            question_data = {
                'id': question.id,
                'order': question.order,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'is_required': question.is_required,
                'options': question.get_options_list(),
                'created_at': question.created_at.isoformat(),
                'statistics': question.get_answer_statistics(),
                'total_answers': question.answers.count()
            }
            questionnaire_data['questions'].append(question_data)
        
        export_data['questionnaires'].append(questionnaire_data)
    
    # Create JSON response
    json_output = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    response = make_response(json_output)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=questionnaires_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    return response