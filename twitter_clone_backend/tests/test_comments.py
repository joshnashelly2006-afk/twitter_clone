def test_comment_lifecycle(client, auth_headers):
    """Test adding, retrieving, updating, and deleting comments."""
    post_res = client.post('/api/v1/posts', json={'content': 'Post for comments'}, headers=auth_headers)
    post_id = post_res.get_json()['data']['id']

    # 1. Add comment
    add_res = client.post(f'/api/v1/posts/{post_id}/comments', json={'comment': 'Nice post!'}, headers=auth_headers)
    assert add_res.status_code == 201
    comment_id = add_res.get_json()['data']['id']

    # 2. Get comments
    get_res = client.get(f'/api/v1/posts/{post_id}/comments')
    assert get_res.status_code == 200
    assert get_res.get_json()['data']['comments_count'] == 1

    # 3. Edit comment
    edit_res = client.put(f'/api/v1/comments/{comment_id}', json={'comment': 'Updated comment'}, headers=auth_headers)
    assert edit_res.status_code == 200
    assert edit_res.get_json()['data']['comment'] == 'Updated comment'

    # 4. Delete comment
    del_res = client.delete(f'/api/v1/comments/{comment_id}', headers=auth_headers)
    assert del_res.status_code == 200
