from app.extensions import db
from app.models.report import Report
from app.models.user import User
from app.models.post import Post
from app.errors import ValidationError, NotFoundError

VALID_REASONS = {'SPAM', 'ABUSE', 'HARASSMENT', 'VIOLENCE', 'OTHER'}


def submit_report(reporter_id, data):
    """
    Submit moderation report for a user or post.
    """
    reason = (data.get('reason') or '').upper()
    if reason not in VALID_REASONS:
        raise ValidationError(f"Invalid report reason. Allowed reasons: {', '.join(VALID_REASONS)}")

    reported_user_id = data.get('reported_user_id')
    reported_post_id = data.get('reported_post_id')

    if not reported_user_id and not reported_post_id:
        raise ValidationError('Must provide either reported_user_id or reported_post_id.')

    if reported_user_id:
        user = User.query.get(reported_user_id)
        if not user:
            raise NotFoundError('Reported user not found.')

    if reported_post_id:
        post = Post.query.get(reported_post_id)
        if not post:
            raise NotFoundError('Reported post not found.')

    report = Report(
        reporter_id=reporter_id,
        reported_user_id=reported_user_id,
        reported_post_id=reported_post_id,
        reason=reason,
        details=data.get('details')
    )

    db.session.add(report)
    db.session.commit()

    return {
        'id': str(report.id),
        'message': 'Report submitted successfully. Administrators will review your report.'
    }
