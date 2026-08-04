def test_bookmark_lifecycle(client, auth_headers):
    """Test bookmarking and unbookmarking a post."""
    post_res = client.post('/api/v1/posts', json={'content': 'Post to bookmark'}, headers=auth_headers)
    post_id = post_res.get_json()['data']['id']

    # 1. Bookmark post
    bm_res = client.post(f'/api/v1/posts/{post_id}/bookmark', headers=auth_headers)
    assert bm_res.status_code == 200
    assert bm_res.get_json()['success'] is True

    # 2. Get bookmarks list
    list_res = client.get('/api/v1/bookmarks', headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.get_json()['data']['posts']) == 1

    # 3. Unbookmark post
    unbm_res = client.delete(f'/api/v1/posts/{post_id}/bookmark', headers=auth_headers)
    assert unbm_res.status_code == 200
    assert unbm_res.get_json()['success'] is True
