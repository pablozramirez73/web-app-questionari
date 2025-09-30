from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory storage for questions and responses
questions = []
responses = []

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/questionnaires')
def questionnaires():
    """List all questionnaires"""
    return render_template('questionnaires.html', questions=questions)

@app.route('/api/questions', methods=['GET', 'POST'])
def api_questions():
    """API endpoint to get or create questions"""
    if request.method == 'GET':
        return jsonify(questions)
    elif request.method == 'POST':
        data = request.get_json()
        question = {
            'id': len(questions) + 1,
            'title': data.get('title'),
            'description': data.get('description'),
            'questions': data.get('questions', [])
        }
        questions.append(question)
        return jsonify(question), 201

@app.route('/api/questions/<int:question_id>', methods=['GET', 'PUT', 'DELETE'])
def api_question_detail(question_id):
    """API endpoint to get, update or delete a specific question"""
    question = next((q for q in questions if q['id'] == question_id), None)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    if request.method == 'GET':
        return jsonify(question)
    elif request.method == 'PUT':
        data = request.get_json()
        question.update({
            'title': data.get('title', question['title']),
            'description': data.get('description', question['description']),
            'questions': data.get('questions', question['questions'])
        })
        return jsonify(question)
    elif request.method == 'DELETE':
        questions.remove(question)
        return jsonify({'message': 'Question deleted'}), 200

@app.route('/api/responses', methods=['GET', 'POST'])
def api_responses():
    """API endpoint to get or create responses"""
    if request.method == 'GET':
        return jsonify(responses)
    elif request.method == 'POST':
        data = request.get_json()
        response = {
            'id': len(responses) + 1,
            'question_id': data.get('question_id'),
            'answers': data.get('answers', [])
        }
        responses.append(response)
        return jsonify(response), 201

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
