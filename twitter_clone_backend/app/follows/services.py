from app.extensions import db
from app.models.follow import Follow
from app.models.user import User
from app.models.block import Block
from app.notifications.services import create_notification
from app.errors import ConflictError, NotFoundError, ForbiddenError
from app.follows.validators import validate_target_user


def follow_user(follower_id, target_id):
    """Follow a target user."""
    target_user = validate_target_user(follower_id, target_id)

    # Check block relationship
    blocked = Block.query.filter(
        ((Block.blocker_id == follower_id) & (Block.blocked_id == target_user.id)) |
        ((Block.blocker_id == target_user.id) & (Block.blocked_id == follower_id))
    ).first()
    if blocked:
        raise ForbiddenError('Action blocked.')

    existing_follow = Follow.query.filter_by(
        follower_id=follower_id,
        following_id=target_user.id
    ).first()

    if existing_follow:
        raise ConflictError('You are already following this user.')

    follow = Follow(
        follower_id=follower_id,
        following_id=target_user.id
    )

    db.session.add(follow)
    db.session.commit()

    # Create notification for target user
    create_notification(
        recipient_id=target_user.id,
        sender_id=follower_id,
        notif_type='FOLLOW'
    )

    followers_count = Follow.query.filter_by(following_id=target_user.id).count()

    return {
        'message': f'You are now following @{target_user.username}.',
        'followers_count': followers_count
    }


def unfollow_user(follower_id, target_id):
    """Unfollow a target user."""
    target_user = validate_target_user(follower_id, target_id)

    existing_follow = Follow.query.filter_by(
        follower_id=follower_id,
        following_id=target_user.id
    ).first()

    if not existing_follow:
        raise NotFoundError('You are not following this user.')

    db.session.delete(existing_follow)
    db.session.commit()

    followers_count = Follow.query.filter_by(following_id=target_user.id).count()

    return {
        'message': f'You have unfollowed @{target_user.username}.',
        'followers_count': followers_count
    }


def get_user_followers(target_id, page=1, per_page=10):
    """
    Retrieve paginated list of users following the target user.
    Optimized to eliminate N+1 queries via bulk user fetching.
    """
    user = User.query.get(target_id)
    if not user or not user.is_active:
        raise NotFoundError('User not found.')

    pagination = Follow.query.filter_by(following_id=user.id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    follower_ids = [f.follower_id for f in pagination.items]
    if follower_ids:
        users = User.query.filter(User.id.in_(follower_ids), User.is_active.is_(True)).all()
        user_map = {u.id: u for u in users}
    else:
        user_map = {}

    followers_list = []
    for follow in pagination.items:
        follower = user_map.get(follow.follower_id)
        if follower:
            followers_list.append({
                'id': str(follower.id),
                'username': follower.username,
                'bio': follower.bio,
                'profile_picture': follower.profile_picture,
                'followed_at': follow.created_at.isoformat()
            })

    total_followers_count = Follow.query.filter_by(following_id=user.id).count()

    return {
        'followers_count': total_followers_count,
        'followers': followers_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def get_user_following(target_id, page=1, per_page=10):
    """
    Retrieve paginated list of users followed by the target user.
    Optimized to eliminate N+1 queries via bulk user fetching.
    """
    user = User.query.get(target_id)
    if not user or not user.is_active:
        raise NotFoundError('User not found.')

    pagination = Follow.query.filter_by(follower_id=user.id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    following_ids = [f.following_id for f in pagination.items]
    if following_ids:
        users = User.query.filter(User.id.in_(following_ids), User.is_active.is_(True)).all()
        user_map = {u.id: u for u in users}
    else:
        user_map = {}

    following_list = []
    for follow in pagination.items:
        followed_user = user_map.get(follow.following_id)
        if followed_user:
            following_list.append({
                'id': str(followed_user.id),
                'username': followed_user.username,
                'bio': followed_user.bio,
                'profile_picture': followed_user.profile_picture,
                'followed_at': follow.created_at.isoformat()
            })

    total_following_count = Follow.query.filter_by(follower_id=user.id).count()

    return {
        'following_count': total_following_count,
        'following': following_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def get_follow_status(current_user_id, target_id):
    """Check mutual follow status between current user and target user."""
    target_user = User.query.get(target_id)
    if not target_user or not target_user.is_active:
        raise NotFoundError('Target user not found.')

    is_following = Follow.query.filter_by(
        follower_id=current_user_id,
        following_id=target_user.id
    ).first() is not None

    is_followed_by = Follow.query.filter_by(
        follower_id=target_user.id,
        following_id=current_user_id
    ).first() is not None

    return {
        'is_following': is_following,
        'is_followed_by': is_followed_by
    }
