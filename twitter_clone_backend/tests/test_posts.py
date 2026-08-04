def test_create_post(client, auth_headers):
    """Test post creation endpoint."""
    payload = {
        'content': 'Hello, world! This is my first tweet.'
    }
    response = client.post('/api/v1/posts', json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['content'] == 'Hello, world! This is my first tweet.'


def test_get_single_post(client, auth_headers):
    """Test fetching a single post by ID."""
    create_res = client.post('/api/v1/posts', json={'content': 'Single post test'}, headers=auth_headers)
    post_id = create_res.get_json()['data']['id']

    response = client.get(f'/api/v1/posts/{post_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['id'] == post_id


def test_delete_post(client, auth_headers):
    """Test post deletion by post owner."""
    create_res = client.post('/api/v1/posts', json={'content': 'Post to delete'}, headers=auth_headers)
    post_id = create_res.get_json()['data']['id']

    response = client.delete(f'/api/v1/posts/{post_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

    get_res = client.get(f'/api/v1/posts/{post_id}')
    assert get_res.status_code == 404
