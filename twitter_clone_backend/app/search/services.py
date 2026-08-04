from app.models.user import User
from app.models.post import Post
from app.models.hashtag import Hashtag, PostHashtag
from app.posts.services import format_posts_batch


def global_search(query_str, search_type='all', current_user_id=None, page=1, per_page=10):
    """
    Search across Users, Posts, and Hashtags.
    """
    query_str = (query_str or '').strip()
    if not query_str:
        return {'users': [], 'posts': [], 'hashtags': []}

    results = {}

    # 1. Search Users
    if search_type in ('all', 'users'):
        u_pagination = User.query.filter(
            User.is_active.is_(True),
            User.username.ilike(f"%{query_str}%")
        ).paginate(page=page, per_page=per_page, error_out=False)

        users_list = [{
            'id': str(u.id),
            'username': u.username,
            'bio': u.bio,
            'profile_picture': u.profile_picture
        } for u in u_pagination.items]
        results['users'] = users_list

    # 2. Search Hashtags
    if search_type in ('all', 'hashtags'):
        clean_tag = query_str.lstrip('#')
        h_pagination = Hashtag.query.filter(
            Hashtag.name.ilike(f"%{clean_tag}%")
        ).order_by(Hashtag.use_count.desc())\
         .paginate(page=page, per_page=per_page, error_out=False)

        hashtags_list = [{
            'id': str(h.id),
            'name': h.name,
            'use_count': h.use_count
        } for h in h_pagination.items]
        results['hashtags'] = hashtags_list

    # 3. Search Posts
    if search_type in ('all', 'posts'):
        if query_str.startswith('#'):
            clean_tag = query_str.lstrip('#').lower()
            hashtag = Hashtag.query.filter_by(name=clean_tag).first()
            if hashtag:
                post_hashtags = PostHashtag.query.filter_by(hashtag_id=hashtag.id).all()
                post_ids = [ph.post_id for ph in post_hashtags]
                p_pagination = Post.query.filter(Post.id.in_(post_ids))\
                    .order_by(Post.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
                posts_list = format_posts_batch(p_pagination.items, current_user_id)
            else:
                posts_list = []
        else:
            p_pagination = Post.query.filter(
                Post.content.ilike(f"%{query_str}%")
            ).order_by(Post.created_at.desc())\
             .paginate(page=page, per_page=per_page, error_out=False)

            posts_list = format_posts_batch(p_pagination.items, current_user_id)

        results['posts'] = posts_list

    return results
