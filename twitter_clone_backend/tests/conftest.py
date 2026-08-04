import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    """Create Flask application configured for testing."""
    _app = create_app('testing')
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a clean database session for a test function."""
    with app.app_context():
        _db.session.begin_nested()
        yield _db.session
        _db.session.rollback()


@pytest.fixture
def auth_headers(client):
    """Fixture to register and log in a test user, returning Bearer auth headers."""
    user_payload = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }
    client.post('/api/v1/auth/register', json=user_payload)
    response = client.post('/api/v1/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'Password123!'
    })
    data = response.get_json()['data']
    access_token = data['access_token']
    return {
        'Authorization': f"Bearer {access_token}"
    }
