from flask import request, jsonify, session
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from werkzeug.exceptions import BadRequest
from datetime import datetime
from app import db
from app.api import bp
from app.models import Questionnaire, Question, Response, Answer
import json
import uuid

@bp.route('/questions', methods=['POST'])
@login_required
def create_question():
    """Create a new question via API"""
    data = request.get_json()
    
    questionnaire = Questionnaire.query.get_or_404(data.get('questionnaire_id'))
    
    # Check permissions
    if questionnaire.creator != current_user and not current_user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    # Validate question data
    if not data.get('question_text') or not data.get('question_type'):
        return jsonify({'error': 'Question text and type are required'}), 400
    
    question = Question(
        questionnaire_id=questionnaire.id,
        question_text=data.get('question_text'),
        question_type=data.get('question_type'),
        is_required=data.get('is_required', True),
        order=data.get('order', 0)
    )
    
    # Handle options for choice questions
    if data.get('question_type') in ['single_choice', 'multiple_choice']:
        options = data.get('options', [])
        if options:
            question.set_options_list([opt for opt in options if opt.strip()])
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'question_text': question.question_text,
        'question_type': question.question_type,
        'options': question.get_options_list(),
        'is_required': question.is_required,
        'order': question.order
    }), 201

@bp.route('/questions/<int:id>', methods=['PUT'])
@login_required
def update_question(id):
    """Update a question via API"""
    question = Question.query.get_or_404(id)
    
    # Check permissions
    if question.questionnaire.creator != current_user and not current_user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Update question fields
    if 'question_text' in data:
        question.question_text = data['question_text']
    if 'question_type' in data:
        question.question_type = data['question_type']
    if 'is_required' in data:
        question.is_required = data['is_required']
    if 'order' in data:
        question.order = data['order']
    
    # Handle options for choice questions
    if question.question_type in ['single_choice', 'multiple_choice'] and 'options' in data:
        options = data.get('options', [])
        question.set_options_list([opt for opt in options if opt.strip()])
    
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'question_text': question.question_text,
        'question_type': question.question_type,
        'options': question.get_options_list(),
        'is_required': question.is_required,
        'order': question.order
    })

@bp.route('/questions/<int:id>', methods=['DELETE'])
@login_required
def delete_question(id):
    """Delete a question via API"""
    question = Question.query.get_or_404(id)
    
    # Check permissions
    if question.questionnaire.creator != current_user and not current_user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'})

@bp.route('/questionnaire/<int:id>/respond', methods=['POST'])
def submit_response(id):
    """Submit response to questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    data = request.get_json()
    
    # Check if questionnaire is active
    if not questionnaire.is_active:
        return jsonify({'error': 'Questionnaire is not active'}), 400
    
    # Determine user or session
    user_id = current_user.id if current_user.is_authenticated else None
    session_id = session.get('session_id')
    
    if not user_id and not questionnaire.allow_anonymous:
        return jsonify({'error': 'Authentication required'}), 401
    
    if not user_id and not session_id:
        # Generate session ID for anonymous users
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    # Check for existing response if multiple submissions not allowed
    if not questionnaire.multiple_submissions:
        existing_response = Response.query.filter_by(
            questionnaire_id=id,
            user_id=user_id,
            is_complete=True
        ).first()
        
        if user_id and existing_response:
            return jsonify({'error': 'You have already completed this questionnaire'}), 400
        
        if not user_id and session_id:
            existing_response = Response.query.filter_by(
                questionnaire_id=id,
                session_id=session_id,
                is_complete=True
            ).first()
            
            if existing_response:
                return jsonify({'error': 'You have already completed this questionnaire'}), 400
    
    # Create response
    response = Response(
        questionnaire_id=id,
        user_id=user_id,
        session_id=session_id if not user_id else None,
        is_complete=True
    )
    db.session.add(response)
    db.session.flush()  # Get response ID
    
    # Process answers
    answers = data.get('answers', {})
    saved_answers = 0
    
    for question_id, answer_data in answers.items():
        question = Question.query.get(int(question_id))
        if not question or question.questionnaire_id != id:
            continue
        
        # Validate required questions
        if question.is_required and not answer_data:
            return jsonify({
                'error': f'Question "{question.question_text}" is required'
            }), 400
        
        if answer_data:  # Only save non-empty answers
            answer = Answer(
                response_id=response.id,
                question_id=question.id
            )
            
            # Handle different question types
            if question.question_type == 'open_ended':
                answer.answer_text = answer_data
            elif question.question_type in ['single_choice', 'multiple_choice', 'scale']:
                # All choice questions now use single selection
                answer.answer_value = str(answer_data)
            
            db.session.add(answer)
            saved_answers += 1
    
    db.session.commit()
    
    return jsonify({
        'message': 'Response submitted successfully',
        'response_id': response.id,
        'answers_saved': saved_answers
    }), 201

@bp.route('/response/<int:id>/answers', methods=['GET'])
@login_required
def get_response_answers(id):
    """Get answers for a specific response"""
    response = Response.query.get_or_404(id)
    
    # Check permissions
    if (response.user != current_user and 
        response.questionnaire.creator != current_user and 
        not current_user.is_admin()):
        return jsonify({'error': 'Permission denied'}), 403
    
    answers = {}
    for answer in response.answers:
        if answer.question.question_type == 'open_ended':
            answers[answer.question_id] = answer.answer_text
        else:
            # All choice questions (single_choice, multiple_choice, scale) now use single values
            answers[answer.question_id] = answer.answer_value
    
    return jsonify({
        'response_id': response.id,
        'questionnaire_id': response.questionnaire_id,
        'answers': answers,
        'submitted_at': response.submitted_at.isoformat(),
        'is_complete': response.is_complete
    })

@bp.route('/questionnaire/<int:id>/statistics', methods=['GET'])
@login_required
def get_questionnaire_statistics(id):
    """Get statistics for a questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Check permissions
    if (questionnaire.creator != current_user and not current_user.is_admin()):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get basic statistics
    total_responses = questionnaire.responses.filter_by(is_complete=True).count()
    
    # Get question statistics
    questions_stats = {}
    for question in questionnaire.questions:
        stats = question.get_answer_statistics()
        questions_stats[question.id] = {
            'question_text': question.question_text,
            'question_type': question.question_type,
            'statistics': stats,
            'total_answers': sum(stats.values()) if stats else 0
        }
    
    return jsonify({
        'questionnaire_id': questionnaire.id,
        'title': questionnaire.title,
        'total_responses': total_responses,
        'questions_statistics': questions_stats
    })

@bp.route('/response/<int:id>/update', methods=['PUT'])
@login_required
def update_response(id):
    """Update an existing response"""
    response = Response.query.get_or_404(id)
    
    # Check permissions
    if (response.user != current_user and 
        response.questionnaire.creator != current_user and 
        not current_user.is_admin()):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    answers = data.get('answers', {})
    
    if not answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    updated_answers = 0
    
    # Update existing answers or create new ones
    for question_id, answer_data in answers.items():
        question = Question.query.get(int(question_id))
        if not question or question.questionnaire_id != response.questionnaire_id:
            continue
        
        # Find existing answer or create new one
        answer = Answer.query.filter_by(
            response_id=response.id,
            question_id=question.id
        ).first()
        
        if not answer:
            answer = Answer(
                response_id=response.id,
                question_id=question.id
            )
            db.session.add(answer)
        
        # Update answer based on question type
        if question.question_type == 'open_ended':
            answer.answer_text = answer_data
            answer.answer_value = None
        else:
            # All choice questions (single_choice, multiple_choice, scale)
            answer.answer_value = str(answer_data)
            answer.answer_text = None
        
        updated_answers += 1
    
    # Remove answers for questions not in the update
    existing_answer_questions = [int(qid) for qid in answers.keys()]
    answers_to_remove = Answer.query.filter(
        Answer.response_id == response.id,
        ~Answer.question_id.in_(existing_answer_questions)
    ).all()
    
    for answer in answers_to_remove:
        db.session.delete(answer)
    
    # Update response timestamp
    response.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Response updated successfully',
        'response_id': response.id,
        'answers_updated': updated_answers,
        'answers_removed': len(answers_to_remove)
    })

@bp.route('/response/<int:id>/delete', methods=['DELETE'])
@login_required  
def delete_response(id):
    """Delete a response (admin only)"""
    response = Response.query.get_or_404(id)
    
    # Check permissions - only admins or questionnaire creators can delete
    if (response.questionnaire.creator != current_user and not current_user.is_admin()):
        return jsonify({'error': 'Permission denied - admin access required'}), 403
    
    # Store info for response
    questionnaire_title = response.questionnaire.title
    respondent_name = response.get_respondent_name()
    
    # Delete response (cascade will delete associated answers)
    db.session.delete(response)
    db.session.commit()
    
    return jsonify({
        'message': f'Response from {respondent_name} deleted successfully',
        'questionnaire': questionnaire_title
    })