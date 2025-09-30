import unittest
from app import create_app, db
from app.models import User, Questionnaire
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(self.app is None)

    def test_database(self):
        u = User(username='test', email='test@example.com')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.username, 'test')

if __name__ == '__main__':
    unittest.main()