import os
from app import create_app, db
from app.models import User, Questionnaire, Question, Response, Answer

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'Questionnaire': Questionnaire,
        'Question': Question,
        'Response': Response,
        'Answer': Answer
    }

@app.cli.command()
def create_admin():
    """Create an admin user"""
    print("Creating admin user...")
    
    username = input("Admin username: ")
    email = input("Admin email: ")
    password = input("Admin password: ")
    
    # Check if user already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        print("User with this username or email already exists!")
        return
    
    admin = User(
        username=username,
        email=email,
        first_name="Admin",
        last_name="User",
        role="admin"
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin user '{username}' created successfully!")

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)