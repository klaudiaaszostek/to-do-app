import unittest
from flask import url_for
from flask_testing import TestCase
from werkzeug.security import generate_password_hash
from app import create_app, db
from models import User, Task
from forms import RegistrationForm, LoginForm, TaskForm
from flask_login import current_user

class TestBase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()
        user = User(username="testuser", email="test@example.com", password_hash=generate_password_hash("password"))
        admin = User(username="admin", email="admin@example.com", password_hash=generate_password_hash("adminpass"), role="admin")
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestModels(TestBase):

    def test_user_model(self):
        user = User.query.filter_by(username="testuser").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_task_model(self):
        user = User.query.filter_by(username="testuser").first()
        task = Task(title="Test Task", description="Just a test task", author=user)
        db.session.add(task)
        db.session.commit()
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.author.username, "testuser")

class TestForms(TestBase):

    def test_registration_form(self):
        form = RegistrationForm(username="newuser", email="new@example.com", password="password", confirm_password="password")
        self.assertTrue(form.validate())

    def test_login_form(self):
        form = LoginForm(email="test@example.com", password="password")
        self.assertTrue(form.validate())

class TestViews(TestBase):

    def test_404_view(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_login_view(self):
        response = self.client.post(url_for('auth.login'), data=dict(
            email="test@example.com", password="password"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout', response.data)

    def test_register_view(self):
        response = self.client.post(url_for('auth.register'), data=dict(
            username="newuser", email="new@example.com", password="password", confirm_password="password"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_task_creation(self):
        self.client.post(url_for('auth.login'), data=dict(
            email="test@example.com", password="password"), follow_redirects=True)
        response = self.client.post(url_for('tasks.new_task'), data=dict(
            title="New Task", description="New task description"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Task', response.data)

class TestAccessControl(TestBase):

    def test_admin_access(self):
        self.client.post(url_for('auth.login'), data=dict(
            email="admin@example.com", password="adminpass"), follow_redirects=True)
        response = self.client.get(url_for('tasks.tasks'))
        self.assertEqual(response.status_code, 200)

    def test_user_access(self):
        self.client.post(url_for('auth.login'), data=dict(
            email="test@example.com", password="password"), follow_redirects=True)
        response = self.client.get(url_for('tasks.tasks'))
        self.assertEqual(response.status_code, 200)

    def test_non_logged_in_access(self):
        response = self.client.get(url_for('tasks.tasks'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

if __name__ == '__main__':
    unittest.main()
