from app.extensions import db
from app.models.like import Like
from app.models.post import Post
from app.models.block import Block
from app.notifications.services import create_notification
from app.errors import NotFoundError, ConflictError, ForbiddenError


def like_post(user_id, post_id):
    """Like a post and dispatch notification to post owner."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    # Check block relationship
    blocked = Block.query.filter(
        ((Block.blocker_id == user_id) & (Block.blocked_id == post.user_id)) |
        ((Block.blocker_id == post.user_id) & (Block.blocked_id == user_id))
    ).first()
    if blocked:
        raise ForbiddenError('Action blocked.')

    existing_like = Like.query.filter_by(user_id=user_id, post_id=post.id).first()
    if existing_like:
        raise ConflictError('You have already liked this post.')

    like = Like(user_id=user_id, post_id=post.id)
    db.session.add(like)
    db.session.commit()

    # Create notification for post author
    create_notification(
        recipient_id=post.user_id,
        sender_id=user_id,
        notif_type='LIKE',
        post_id=post.id
    )

    likes_count = Like.query.filter_by(post_id=post.id).count()

    return {
        'message': 'Post liked successfully.',
        'likes_count': likes_count,
        'liked': True
    }


def unlike_post(user_id, post_id):
    """Unlike a post."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    existing_like = Like.query.filter_by(user_id=user_id, post_id=post.id).first()
    if not existing_like:
        raise NotFoundError('You have not liked this post.')

    db.session.delete(existing_like)
    db.session.commit()

    likes_count = Like.query.filter_by(post_id=post.id).count()

    return {
        'message': 'Post unliked successfully.',
        'likes_count': likes_count,
        'liked': False
    }


def get_post_likes(post_id, page=1, per_page=10):
    """Retrieve paginated list of users who liked a post."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    pagination = Like.query.filter_by(post_id=post.id)\
        .order_by(Like.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    likers_list = []
    for like in pagination.items:
        likers_list.append({
            'id': str(like.user.id),
            'username': like.user.username,
            'bio': like.user.bio,
            'profile_picture': like.user.profile_picture,
            'liked_at': like.created_at.isoformat()
        })

    total_likes = Like.query.filter_by(post_id=post.id).count()

    return {
        'likes_count': total_likes,
        'likers': likers_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def check_user_liked_post(user_id, post_id):
    """Check if specified user liked the target post."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    liked = Like.query.filter_by(user_id=user_id, post_id=post.id).first() is not None

    return {'liked': liked}
