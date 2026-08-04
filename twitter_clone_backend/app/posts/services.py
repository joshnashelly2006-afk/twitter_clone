import re
from sqlalchemy import func
from app.extensions import db
from app.models.post import Post
from app.models.user import User
from app.models.like import Like
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.hashtag import Hashtag, PostHashtag
from app.models.block import Block
from app.notifications.services import create_notification
from app.errors import NotFoundError, ForbiddenError, ValidationError
from app.posts.utils import save_uploaded_file, delete_uploaded_file


def process_hashtags_and_mentions(post):
    """
    Parse #hashtags and @mentions automatically from post content text.
    """
    if not post.content:
        return

    # 1. Parse Hashtags (#tag)
    raw_hashtags = set(re.findall(r'#(\w+)', post.content))
    for tag_name in raw_hashtags:
        clean_tag = tag_name.lower()
        hashtag = Hashtag.query.filter_by(name=clean_tag).first()
        if not hashtag:
            hashtag = Hashtag(name=clean_tag, use_count=1)
            db.session.add(hashtag)
            db.session.flush()
        else:
            hashtag.use_count += 1

        post_tag = PostHashtag(post_id=post.id, hashtag_id=hashtag.id)
        db.session.add(post_tag)

    # 2. Parse Mentions (@username)
    raw_mentions = set(re.findall(r'@(\w+)', post.content))
    for username in raw_mentions:
        mentioned_user = User.query.filter_by(username=username, is_active=True).first()
        if mentioned_user and str(mentioned_user.id) != str(post.user_id):
            # Check block relationship before dispatching notification
            blocked = Block.query.filter(
                ((Block.blocker_id == post.user_id) & (Block.blocked_id == mentioned_user.id)) |
                ((Block.blocker_id == mentioned_user.id) & (Block.blocked_id == post.user_id))
            ).first()

            if not blocked:
                create_notification(
                    recipient_id=mentioned_user.id,
                    sender_id=post.user_id,
                    notif_type='MENTION',
                    post_id=post.id
                )


def format_post_dict(post, current_user_id=None):
    """Format single Post model instance to JSON dictionary."""
    author = User.query.get(post.user_id)
    author_dict = {
        'id': str(author.id),
        'username': author.username,
        'bio': author.bio,
        'profile_picture': author.profile_picture
    } if author else None

    likes_count = Like.query.filter_by(post_id=post.id).count()
    comments_count = Comment.query.filter_by(post_id=post.id).count()

    liked_by_me = False
    if current_user_id:
        liked_by_me = Like.query.filter_by(user_id=current_user_id, post_id=post.id).first() is not None

    return {
        'post_id': str(post.id),
        'id': str(post.id),
        'user_id': str(post.user_id),
        'author': author_dict,
        'content': post.content,
        'media_path': post.media_path,
        'media_type': post.media_type,
        'likes_count': likes_count,
        'comments_count': comments_count,
        'liked_by_me': liked_by_me,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat()
    }


def format_posts_batch(posts, current_user_id=None):
    """
    Format a list of Post model instances efficiently without N+1 database queries.
    Uses bulk queries to pre-fetch authors, counts, and liked status in 4 total queries.
    """
    if not posts:
        return []

    post_ids = [p.id for p in posts]
    author_ids = list({p.user_id for p in posts})

    # 1. Batch fetch authors
    authors = User.query.filter(User.id.in_(author_ids)).all()
    author_map = {
        a.id: {
            'id': str(a.id),
            'username': a.username,
            'bio': a.bio,
            'profile_picture': a.profile_picture
        }
        for a in authors
    }

    # 2. Batch fetch likes counts
    likes_counts_query = db.session.query(
        Like.post_id, func.count(Like.id)
    ).filter(Like.post_id.in_(post_ids)).group_by(Like.post_id).all()
    likes_count_map = {post_id: count for post_id, count in likes_counts_query}

    # 3. Batch fetch comments counts
    comments_counts_query = db.session.query(
        Comment.post_id, func.count(Comment.id)
    ).filter(Comment.post_id.in_(post_ids)).group_by(Comment.post_id).all()
    comments_count_map = {post_id: count for post_id, count in comments_counts_query}

    # 4. Batch fetch liked_by_me status if current_user_id provided
    liked_post_ids = set()
    if current_user_id:
        user_likes = Like.query.filter(
            Like.user_id == current_user_id,
            Like.post_id.in_(post_ids)
        ).all()
        liked_post_ids = {l.post_id for l in user_likes}

    formatted_list = []
    for post in posts:
        formatted_list.append({
            'post_id': str(post.id),
            'id': str(post.id),
            'user_id': str(post.user_id),
            'author': author_map.get(post.user_id),
            'content': post.content,
            'media_path': post.media_path,
            'media_type': post.media_type,
            'likes_count': likes_count_map.get(post.id, 0),
            'comments_count': comments_count_map.get(post.id, 0),
            'liked_by_me': post.id in liked_post_ids,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat()
        })

    return formatted_list


def create_post(user_id, content, file_storage):
    """
    Create a new post with optional image/video media attachment.
    """
    user = User.query.get(user_id)
    if not user or not user.is_active or user.is_suspended:
        raise NotFoundError('User account not found or suspended.')

    media_path = None
    media_type = None

    if file_storage and file_storage.filename:
        media_path, media_type = save_uploaded_file(file_storage)

    post = Post(
        user_id=user.id,
        content=content or '',
        media_path=media_path,
        media_type=media_type
    )

    db.session.add(post)
    db.session.flush()

    # Process hashtags and mentions
    process_hashtags_and_mentions(post)

    db.session.commit()

    return format_post_dict(post, current_user_id=user_id)


def get_post_by_id(post_id, current_user_id=None):
    """Retrieve single post details by UUID."""
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    return format_post_dict(post, current_user_id=current_user_id)


def get_my_posts(current_user_id, page=1, per_page=10):
    """
    Retrieve logged-in user's posts sorted newest first with pagination.
    """
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        raise NotFoundError('User account not found.')

    pagination = Post.query.filter_by(user_id=user.id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    post_list = format_posts_batch(pagination.items, current_user_id)

    return {
        'posts': post_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def get_user_posts(target_user_id, current_user_id=None, page=1, per_page=10):
    """
    Retrieve public posts for a specific user sorted newest first with pagination.
    """
    user = User.query.get(target_user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    pagination = Post.query.filter_by(user_id=user.id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    post_list = format_posts_batch(pagination.items, current_user_id)

    return {
        'posts': post_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def get_personalized_feed(current_user_id, page=1, per_page=10):
    """
    Retrieve personalized feed containing posts from followed users + own posts, sorted newest first.
    """
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        raise NotFoundError('User account not found.')

    # Get list of user IDs followed by current user
    following_records = Follow.query.filter_by(follower_id=user.id).all()
    followed_user_ids = [f.following_id for f in following_records]
    followed_user_ids.append(user.id)  # Include own posts

    pagination = Post.query.filter(Post.user_id.in_(followed_user_ids))\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    post_list = format_posts_batch(pagination.items, current_user_id)

    return {
        'posts': post_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def get_explore_feed(current_user_id=None, page=1, per_page=10):
    """
    Retrieve global explore feed containing latest public posts, sorted newest first.
    """
    pagination = Post.query.order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    post_list = format_posts_batch(pagination.items, current_user_id)

    return {
        'posts': post_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def update_post(post_id, current_user_id, content_str, file_storage, remove_media):
    """
    Update post content or replace/remove media attachment.
    Enforces post ownership check.
    """
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    if str(post.user_id) != str(current_user_id):
        raise ForbiddenError('You are not authorized to edit this post.')

    if content_str is not None:
        post.content = content_str

    if file_storage and file_storage.filename:
        if post.media_path:
            delete_uploaded_file(post.media_path)

        new_media_path, new_media_type = save_uploaded_file(file_storage)
        post.media_path = new_media_path
        post.media_type = new_media_type
    elif remove_media:
        if post.media_path:
            delete_uploaded_file(post.media_path)
        post.media_path = None
        post.media_type = None

    if not post.content and not post.media_path:
        raise ValidationError('Post content and media cannot both be empty.')

    db.session.commit()

    return format_post_dict(post, current_user_id=current_user_id)


def delete_post(post_id, current_user_id):
    """
    Delete post and its associated media file from server disk.
    Enforces post ownership check.
    """
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found.')

    if str(post.user_id) != str(current_user_id):
        raise ForbiddenError('You are not authorized to delete this post.')

    if post.media_path:
        delete_uploaded_file(post.media_path)

    db.session.delete(post)
    db.session.commit()

    return {
        'id': str(post_id),
        'message': 'Post deleted successfully.'
    }
