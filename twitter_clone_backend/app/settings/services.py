from app.extensions import db
from app.models.user_settings import UserSettings


def get_settings(user_id):
    """Get or create user settings preferences."""
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()

    return {
        'dark_mode': settings.dark_mode,
        'is_private': settings.is_private,
        'email_notifications': settings.email_notifications,
        'push_notifications': settings.push_notifications,
        'language': settings.language
    }


def update_settings(user_id, data):
    """Update user preferences."""
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)

    if 'dark_mode' in data:
        settings.dark_mode = bool(data['dark_mode'])
    if 'is_private' in data:
        settings.is_private = bool(data['is_private'])
    if 'email_notifications' in data:
        settings.email_notifications = bool(data['email_notifications'])
    if 'push_notifications' in data:
        settings.push_notifications = bool(data['push_notifications'])
    if 'language' in data and data['language']:
        settings.language = str(data['language'])[:10]

    db.session.commit()

    return get_settings(user_id)
