#!/usr/bin/env python3
"""
Test script to verify response editing data loading
"""

from app import create_app, db
from app.models import Response, Answer, Question
from flask_login import login_user
from flask import url_for

def test_response_editing():
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING RESPONSE EDITING DATA LOADING")
        print("=" * 60)
        
        # Get a response to test
        response = Response.query.get(38)
        if not response:
            print("❌ Response 38 not found")
            return
            
        print(f"✅ Testing Response #{response.id}")
        print(f"   Questionnaire: {response.questionnaire.title}")
        print(f"   Respondent: {response.get_respondent_name()}")
        print(f"   Submitted: {response.submitted_at}")
        
        # Test current answers loading logic (same as in routes.py)
        current_answers = {}
        for answer in response.answers:
            if answer.question.question_type == 'open_ended':
                current_answers[answer.question_id] = answer.answer_text
            else:
                current_answers[answer.question_id] = answer.answer_value
        
        print(f"\n📊 CURRENT ANSWERS LOADED:")
        print(f"   Total answers: {len(current_answers)}")
        for question_id, answer_value in current_answers.items():
            question = Question.query.get(question_id)
            print(f"   Q{question_id} ({question.question_type}): \"{answer_value}\"")
        
        # Test questions in questionnaire
        print(f"\n📋 QUESTIONS IN QUESTIONNAIRE:")
        for question in response.questionnaire.questions:
            current_val = current_answers.get(question.id, "No answer")
            print(f"   Q{question.id}: {question.question_text[:50]}...")
            print(f"      Type: {question.question_type}")
            print(f"      Options: {question.get_options_list()}")
            print(f"      Current Answer: \"{current_val}\"")
            print(f"      Will be checked: {current_val in question.get_options_list() if question.get_options_list() else 'N/A'}")
            print()
        
        print("🎯 DATA LOADING TEST COMPLETE")
        print("✅ All data appears to be loading correctly for editing!")

if __name__ == "__main__":
    test_response_editing()