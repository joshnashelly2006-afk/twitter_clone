from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.errors import NotFoundError, ForbiddenError


def create_notification(recipient_id, sender_id, notif_type, post_id=None):
    """
    Create a notification if recipient is not sender.
    """
    if str(recipient_id) == str(sender_id):
        return None

    notification = Notification(
        recipient_id=recipient_id,
        sender_id=sender_id,
        type=notif_type,
        post_id=post_id
    )

    db.session.add(notification)
    db.session.commit()
    return notification


def get_user_notifications(user_id, page=1, per_page=10):
    """
    Retrieve paginated notifications for logged-in user.
    Optimized to eliminate N+1 queries via bulk sender user fetching.
    """
    pagination = Notification.query.filter_by(recipient_id=user_id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    sender_ids = list({n.sender_id for n in pagination.items})
    if sender_ids:
        senders = User.query.filter(User.id.in_(sender_ids)).all()
        sender_map = {s.id: s for s in senders}
    else:
        sender_map = {}

    notif_list = []
    for n in pagination.items:
        sender = sender_map.get(n.sender_id)
        notif_list.append({
            'id': str(n.id),
            'type': n.type,
            'post_id': str(n.post_id) if n.post_id else None,
            'is_read': n.is_read,
            'sender': {
                'id': str(sender.id),
                'username': sender.username,
                'profile_picture': sender.profile_picture
            } if sender else None,
            'created_at': n.created_at.isoformat()
        })

    unread_count = Notification.query.filter_by(recipient_id=user_id, is_read=False).count()

    return {
        'unread_count': unread_count,
        'notifications': notif_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def get_unread_count(user_id):
    """Get unread notifications count."""
    count = Notification.query.filter_by(recipient_id=user_id, is_read=False).count()
    return {'unread_count': count}


def mark_notification_as_read(notification_id, user_id):
    """Mark single notification as read."""
    notif = Notification.query.get(notification_id)
    if not notif:
        raise NotFoundError('Notification not found.')

    if str(notif.recipient_id) != str(user_id):
        raise ForbiddenError('Unauthorized.')

    notif.is_read = True
    db.session.commit()
    return {'message': 'Notification marked as read.'}


def mark_all_notifications_as_read(user_id):
    """Mark all unread notifications for user as read."""
    Notification.query.filter_by(recipient_id=user_id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return {'message': 'All notifications marked as read.'}


def delete_notification(notification_id, user_id):
    """Delete a notification."""
    notif = Notification.query.get(notification_id)
    if not notif:
        raise NotFoundError('Notification not found.')

    if str(notif.recipient_id) != str(user_id):
        raise ForbiddenError('Unauthorized.')

    db.session.delete(notif)
    db.session.commit()
    return {'message': 'Notification deleted successfully.'}
