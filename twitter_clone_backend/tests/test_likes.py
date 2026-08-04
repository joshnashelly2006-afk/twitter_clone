def test_like_and_unlike_post(client, auth_headers):
    """Test liking and unliking a post."""
    post_res = client.post('/api/v1/posts', json={'content': 'Post to like'}, headers=auth_headers)
    post_id = post_res.get_json()['data']['id']

    # Like post
    like_res = client.post(f'/api/v1/posts/{post_id}/like', headers=auth_headers)
    assert like_res.status_code == 200
    like_data = like_res.get_json()
    assert like_data['data']['liked'] is True
    assert like_data['data']['likes_count'] == 1

    # Check liked status
    status_res = client.get(f'/api/v1/posts/{post_id}/liked', headers=auth_headers)
    assert status_res.status_code == 200
    assert status_res.get_json()['data']['liked'] is True

    # Unlike post
    unlike_res = client.delete(f'/api/v1/posts/{post_id}/like', headers=auth_headers)
    assert unlike_res.status_code == 200
    unlike_data = unlike_res.get_json()
    assert unlike_data['data']['liked'] is False
    assert unlike_data['data']['likes_count'] == 0
