from app.models.post import Post
from app.errors import NotFoundError


def validate_post_exists(post_id):
    """Ensure target post exists in database."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')
    return post
