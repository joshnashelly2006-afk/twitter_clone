from app.extensions import db
from app.models.block import Block
from app.models.user import User
from app.errors import NotFoundError, ValidationError, ConflictError


def block_user(blocker_id, target_id):
    """Block a target user."""
    if str(blocker_id) == str(target_id):
        raise ValidationError('You cannot block yourself.')

    target_user = User.query.get(target_id)
    if not target_user or not target_user.is_active:
        raise NotFoundError('Target user not found.')

    existing = Block.query.filter_by(blocker_id=blocker_id, blocked_id=target_user.id).first()
    if existing:
        raise ConflictError('You have already blocked this user.')

    block = Block(blocker_id=blocker_id, blocked_id=target_user.id)
    db.session.add(block)
    db.session.commit()

    return {'message': f'You have blocked @{target_user.username}.'}


def unblock_user(blocker_id, target_id):
    """Unblock a target user."""
    if str(blocker_id) == str(target_id):
        raise ValidationError('Invalid user.')

    target_user = User.query.get(target_id)
    if not target_user:
        raise NotFoundError('Target user not found.')

    existing = Block.query.filter_by(blocker_id=blocker_id, blocked_id=target_user.id).first()
    if not existing:
        raise NotFoundError('You have not blocked this user.')

    db.session.delete(existing)
    db.session.commit()

    return {'message': f'You have unblocked @{target_user.username}.'}


def get_blocked_users(blocker_id, page=1, per_page=10):
    """Retrieve paginated list of users blocked by logged-in user."""
    pagination = Block.query.filter_by(blocker_id=blocker_id)\
        .order_by(Block.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    blocked_list = []
    for b in pagination.items:
        user = User.query.get(b.blocked_id)
        if user:
            blocked_list.append({
                'id': str(user.id),
                'username': user.username,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'blocked_at': b.created_at.isoformat()
            })

    return {
        'blocked_users': blocked_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def is_blocked_between(user_a, user_b):
    """Check if either user_a blocked user_b OR user_b blocked user_a."""
    if not user_a or not user_b:
        return False

    b1 = Block.query.filter_by(blocker_id=user_a, blocked_id=user_b).first()
    if b1:
        return True

    b2 = Block.query.filter_by(blocker_id=user_b, blocked_id=user_a).first()
    return b2 is not None
