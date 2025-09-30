from app import create_app, db
from app.models import User, Questionnaire, Question, Choice, Answer

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Questionnaire': Questionnaire, 'Question': Question, 'Choice': Choice, 'Answer': Answer}

if __name__ == '__main__':
    app.run(debug=True)