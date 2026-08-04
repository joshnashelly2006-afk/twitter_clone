from app.extensions import db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.models.block import Block
from app.notifications.services import create_notification
from app.errors import NotFoundError, ForbiddenError


def add_comment(user_id, post_id, comment_text):
    """Add comment to post and notify post author."""
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

    comment = Comment(
        user_id=user_id,
        post_id=post.id,
        comment=comment_text
    )

    db.session.add(comment)
    db.session.commit()

    # Create notification for post author
    create_notification(
        recipient_id=post.user_id,
        sender_id=user_id,
        notif_type='COMMENT',
        post_id=post.id
    )

    user = User.query.get(user_id)
    return {
        'id': str(comment.id),
        'post_id': str(comment.post_id),
        'user_id': str(comment.user_id),
        'author': {
            'id': str(user.id),
            'username': user.username,
            'bio': user.bio,
            'profile_picture': user.profile_picture
        },
        'comment': comment.comment,
        'created_at': comment.created_at.isoformat(),
        'updated_at': comment.updated_at.isoformat()
    }


def get_post_comments(post_id, page=1, per_page=10):
    """Retrieve paginated comments list for a post."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    pagination = Comment.query.filter_by(post_id=post.id)\
        .order_by(Comment.created_at.asc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    comments_list = []
    for comment in pagination.items:
        comments_list.append({
            'id': str(comment.id),
            'post_id': str(comment.post_id),
            'user_id': str(comment.user_id),
            'author': {
                'id': str(comment.user.id),
                'username': comment.user.username,
                'bio': comment.user.bio,
                'profile_picture': comment.user.profile_picture
            },
            'comment': comment.comment,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat()
        })

    total_comments = Comment.query.filter_by(post_id=post.id).count()

    return {
        'comments_count': total_comments,
        'comments': comments_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def update_comment(comment_id, user_id, comment_text):
    """Update comment text (comment author only)."""
    comment = Comment.query.get(comment_id)
    if not comment:
        raise NotFoundError('Comment not found.')

    if str(comment.user_id) != str(user_id):
        raise ForbiddenError('You are not authorized to edit this comment.')

    comment.comment = comment_text
    db.session.commit()

    return {
        'id': str(comment.id),
        'post_id': str(comment.post_id),
        'user_id': str(comment.user_id),
        'comment': comment.comment,
        'created_at': comment.created_at.isoformat(),
        'updated_at': comment.updated_at.isoformat()
    }


def delete_comment(comment_id, user_id):
    """Delete comment (comment author only)."""
    comment = Comment.query.get(comment_id)
    if not comment:
        raise NotFoundError('Comment not found.')

    if str(comment.user_id) != str(user_id):
        raise ForbiddenError('You are not authorized to delete this comment.')

    db.session.delete(comment)
    db.session.commit()

    return {
        'id': str(comment_id),
        'message': 'Comment deleted successfully.'
    }
