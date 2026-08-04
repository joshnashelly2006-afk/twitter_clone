from sqlalchemy import func
from app.extensions import db
from app.models.hashtag import Hashtag
from app.models.post import Post
from app.models.user import User
from app.models.like import Like
from app.models.comment import Comment
from app.models.follow import Follow
from app.posts.services import format_posts_batch
from app.errors import NotFoundError


def get_trending_hashtags(limit=10):
    """Retrieve top trending hashtags ordered by usage frequency."""
    hashtags = Hashtag.query.order_by(Hashtag.use_count.desc()).limit(limit).all()
    return [{
        'id': str(h.id),
        'name': h.name,
        'use_count': h.use_count
    } for h in hashtags]


def get_trending_posts(limit=10, current_user_id=None):
    """
    Retrieve trending posts sorted by combined engagement (likes + comments).
    """
    # Query posts ordered by likes count
    top_post_ids_query = db.session.query(
        Like.post_id, func.count(Like.id).label('like_cnt')
    ).group_by(Like.post_id).order_by(func.count(Like.id).desc()).limit(limit * 2).all()

    if top_post_ids_query:
        post_ids = [p_id for p_id, _ in top_post_ids_query]
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).limit(limit).all()

    formatted_posts = format_posts_batch(posts[:limit], current_user_id)
    return formatted_posts


def get_trending_users(limit=10):
    """Retrieve trending users based on follower count."""
    top_followers_query = db.session.query(
        Follow.following_id, func.count(Follow.id).label('follower_cnt')
    ).group_by(Follow.following_id).order_by(func.count(Follow.id).desc()).limit(limit).all()

    if top_followers_query:
        user_ids = [u_id for u_id, _ in top_followers_query]
        users = User.query.filter(User.id.in_(user_ids), User.is_active.is_(True)).all()
    else:
        users = User.query.filter_by(is_active=True).order_by(User.created_at.desc()).limit(limit).all()

    users_list = []
    for u in users:
        followers_count = Follow.query.filter_by(following_id=u.id).count()
        users_list.append({
            'id': str(u.id),
            'username': u.username,
            'bio': u.bio,
            'profile_picture': u.profile_picture,
            'followers_count': followers_count
        })

    return users_list


def get_user_analytics(user_id):
    """
    Calculate account analytics including total posts, followers gained, and engagement rate.
    """
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise NotFoundError('User account not found.')

    total_posts = Post.query.filter_by(user_id=user.id).count()
    followers_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    # Calculate total engagement received across all user's posts
    user_posts = Post.query.filter_by(user_id=user.id).all()
    user_post_ids = [p.id for p in user_posts]

    total_likes_received = 0
    total_comments_received = 0
    if user_post_ids:
        total_likes_received = Like.query.filter(Like.post_id.in_(user_post_ids)).count()
        total_comments_received = Comment.query.filter(Comment.post_id.in_(user_post_ids)).count()

    total_engagement = total_likes_received + total_comments_received
    engagement_rate = round((total_engagement / total_posts), 2) if total_posts > 0 else 0.0

    return {
        'total_posts': total_posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'total_likes_received': total_likes_received,
        'total_comments_received': total_comments_received,
        'total_engagement': total_engagement,
        'engagement_rate_per_post': engagement_rate
    }
