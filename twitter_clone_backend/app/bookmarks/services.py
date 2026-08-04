from app.extensions import db
from app.models.bookmark import Bookmark
from app.models.post import Post
from app.errors import NotFoundError, ConflictError
from app.posts.services import format_posts_batch


def bookmark_post(user_id, post_id):
    """Bookmark a post for the authenticated user."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    existing = Bookmark.query.filter_by(user_id=user_id, post_id=post.id).first()
    if existing:
        raise ConflictError('Post is already bookmarked.')

    bookmark = Bookmark(user_id=user_id, post_id=post.id)
    db.session.add(bookmark)
    db.session.commit()

    return {'message': 'Post bookmarked successfully.'}


def unbookmark_post(user_id, post_id):
    """Remove bookmark for the authenticated user."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    bookmark = Bookmark.query.filter_by(user_id=user_id, post_id=post.id).first()
    if not bookmark:
        raise NotFoundError('Bookmark record not found.')

    db.session.delete(bookmark)
    db.session.commit()

    return {'message': 'Bookmark removed successfully.'}


def get_user_bookmarks(user_id, page=1, per_page=10):
    """Retrieve paginated bookmarked posts for authenticated user."""
    pagination = Bookmark.query.filter_by(user_id=user_id)\
        .order_by(Bookmark.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    post_ids = [b.post_id for b in pagination.items]
    posts = Post.query.filter(Post.id.in_(post_ids)).all() if post_ids else []

    formatted_posts = format_posts_batch(posts, current_user_id=user_id)

    return {
        'posts': formatted_posts,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }
