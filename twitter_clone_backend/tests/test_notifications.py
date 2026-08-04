def test_notifications_unread_count(client, auth_headers):
    """Test notifications unread count endpoint."""
    response = client.get('/api/v1/notifications/unread-count', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'unread_count' in data['data']
