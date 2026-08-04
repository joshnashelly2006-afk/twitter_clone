def test_block_user_lifecycle(client, auth_headers):
    """Test blocking and unblocking users."""
    target_payload = {
        'username': 'blocktarget',
        'email': 'blocktarget@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }
    reg_res = client.post('/api/v1/auth/register', json=target_payload)
    target_id = reg_res.get_json()['data']['id']

    # Block user
    block_res = client.post(f'/api/v1/users/{target_id}/block', headers=auth_headers)
    assert block_res.status_code == 200
    assert block_res.get_json()['success'] is True

    # List blocks
    list_res = client.get('/api/v1/blocks', headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.get_json()['data']['blocked_users']) == 1

    # Unblock user
    unblock_res = client.delete(f'/api/v1/users/{target_id}/block', headers=auth_headers)
    assert unblock_res.status_code == 200
