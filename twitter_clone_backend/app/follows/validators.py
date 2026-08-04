from app.models.user import User
from app.errors import NotFoundError, ValidationError


def validate_target_user(current_user_id, target_user_id):
    """Validate target user existence and prevent self-follow."""
    if str(current_user_id) == str(target_user_id):
        raise ValidationError('You cannot follow or unfollow yourself.')

    target_user = User.query.get(target_user_id)
    if not target_user or not target_user.is_active:
        raise NotFoundError('Target user not found.')

    return target_user
