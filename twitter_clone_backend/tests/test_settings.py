def test_user_settings_update(client, auth_headers):
    """Test retrieving and updating user preferences."""
    get_res = client.get('/api/v1/settings', headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.get_json()['data']['dark_mode'] is False

    update_payload = {
        'dark_mode': True,
        'language': 'es'
    }
    put_res = client.put('/api/v1/settings', json=update_payload, headers=auth_headers)
    assert put_res.status_code == 200
    data = put_res.get_json()['data']
    assert data['dark_mode'] is True
    assert data['language'] == 'es'
