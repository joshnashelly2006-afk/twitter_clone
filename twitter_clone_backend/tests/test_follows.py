def test_follow_and_unfollow_user(client, auth_headers):
    """Test follow and unfollow relationships."""
    # Register second user
    target_payload = {
        'username': 'targetuser',
        'email': 'target@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }
    reg_res = client.post('/api/v1/auth/register', json=target_payload)
    target_id = reg_res.get_json()['data']['id']

    # Follow target user
    follow_res = client.post(f'/api/v1/users/{target_id}/follow', headers=auth_headers)
    assert follow_res.status_code == 200
    assert follow_res.get_json()['data']['followers_count'] == 1

    # Check status
    status_res = client.get(f'/api/v1/users/{target_id}/follow-status', headers=auth_headers)
    assert status_res.status_code == 200
    assert status_res.get_json()['data']['is_following'] is True

    # Unfollow target user
    unfollow_res = client.delete(f'/api/v1/users/{target_id}/follow', headers=auth_headers)
    assert unfollow_res.status_code == 200
    assert unfollow_res.get_json()['data']['followers_count'] == 0
