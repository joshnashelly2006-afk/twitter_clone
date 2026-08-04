from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.report import Report
from app.errors import ForbiddenError, NotFoundError, ValidationError


def verify_admin(user_id):
    """Verify user is an active system administrator."""
    user = User.query.get(user_id)
    if not user or not user.is_active or not user.is_admin:
        raise ForbiddenError('Administrator privileges required.')
    return user


def get_dashboard_stats(admin_user_id):
    """Get system administrator overview analytics."""
    verify_admin(admin_user_id)

    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True, is_suspended=False).count()
    suspended_users = User.query.filter_by(is_suspended=True).count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    pending_reports = Report.query.filter_by(status='PENDING').count()

    return {
        'total_users': total_users,
        'active_users': active_users,
        'suspended_users': suspended_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'pending_reports': pending_reports
    }


def list_all_users(admin_user_id, page=1, per_page=10):
    """List all registered users for administration."""
    verify_admin(admin_user_id)

    pagination = User.query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    users_list = []
    for u in pagination.items:
        users_list.append({
            'id': str(u.id),
            'username': u.username,
            'email': u.email,
            'is_active': u.is_active,
            'is_admin': u.is_admin,
            'is_suspended': u.is_suspended,
            'created_at': u.created_at.isoformat()
        })

    return {
        'users': users_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def toggle_user_suspension(admin_user_id, target_user_id, suspend=True):
    """Suspend or unsuspend a user account."""
    verify_admin(admin_user_id)

    target_user = User.query.get(target_user_id)
    if not target_user:
        raise NotFoundError('Target user not found.')

    if target_user.is_admin:
        raise ForbiddenError('Cannot suspend an administrator account.')

    target_user.is_suspended = suspend
    db.session.commit()

    action_str = 'suspended' if suspend else 'unsuspended'
    return {'message': f'User @{target_user.username} account has been {action_str}.'}


def list_reports(admin_user_id, status='PENDING', page=1, per_page=10):
    """
    List content moderation reports.
    Optimized to eliminate N+1 queries via bulk user fetching.
    """
    verify_admin(admin_user_id)

    query = Report.query
    if status:
        query = query.filter_by(status=status.upper())

    pagination = query.order_by(Report.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    reporter_ids = list({r.reporter_id for r in pagination.items})
    if reporter_ids:
        reporters = User.query.filter(User.id.in_(reporter_ids)).all()
        reporter_map = {u.id: u for u in reporters}
    else:
        reporter_map = {}

    reports_list = []
    for r in pagination.items:
        reporter = reporter_map.get(r.reporter_id)
        reports_list.append({
            'id': str(r.id),
            'reporter': {'id': str(reporter.id), 'username': reporter.username} if reporter else None,
            'reported_user_id': str(r.reported_user_id) if r.reported_user_id else None,
            'reported_post_id': str(r.reported_post_id) if r.reported_post_id else None,
            'reason': r.reason,
            'details': r.details,
            'status': r.status,
            'created_at': r.created_at.isoformat()
        })

    return {
        'reports': reports_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def resolve_report(admin_user_id, report_id, status='RESOLVED'):
    """Resolve or dismiss a moderation report."""
    verify_admin(admin_user_id)

    status = (status or '').upper()
    if status not in ('RESOLVED', 'DISMISSED'):
        raise ValidationError('Invalid status. Must be RESOLVED or DISMISSED.')

    report = Report.query.get(report_id)
    if not report:
        raise NotFoundError('Report not found.')

    report.status = status
    db.session.commit()

    return {'message': f'Report {report_id} updated to {status}.'}


def admin_delete_post(admin_user_id, post_id):
    """Administrative force deletion of a post."""
    verify_admin(admin_user_id)

    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    db.session.delete(post)
    db.session.commit()

    return {'message': f'Post {post_id} deleted by administrator.'}
