def test_user_registration(client):
    """Test user registration endpoint."""
    payload = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }
    response = client.post('/api/v1/auth/register', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['username'] == 'alice'
    assert data['data']['email'] == 'alice@example.com'


def test_duplicate_registration_error(client):
    """Test registering a duplicate username or email returns 409 Conflict."""
    payload = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }
    client.post('/api/v1/auth/register', json=payload)
    response = client.post('/api/v1/auth/register', json=payload)
    assert response.status_code == 409
    data = response.get_json()
    assert data['success'] is False


def test_user_login(client):
    """Test valid user login and token generation."""
    reg_payload = {
        'username': 'charlie',
        'email': 'charlie@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }
    client.post('/api/v1/auth/register', json=reg_payload)

    login_payload = {
        'email': 'charlie@example.com',
        'password': 'Password123!'
    }
    response = client.post('/api/v1/auth/login', json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']


def test_invalid_login_credentials(client):
    """Test login with wrong password returns 401 Unauthorized."""
    payload = {
        'email': 'charlie@example.com',
        'password': 'WrongPassword'
    }
    response = client.post('/api/v1/auth/login', json=payload)
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_get_me_profile(client, auth_headers):
    """Test authenticated user profile endpoint."""
    response = client.get('/api/v1/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['email'] == 'testuser@example.com'
