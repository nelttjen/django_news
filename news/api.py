from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseForbidden

from news.models import Post, Like
from news.util import is_ajax, get_posts_for_user, get_user_by_token, check_user_token_valid, get_posts_default
from news.util import AJAX_MAX_POSTS


def ajax_load_more_news(request):
    try:
        assert is_ajax(request)
        assert request.method == 'POST'
        post_id = request.POST.get('post_id')
        user_token = request.POST.get('user_token')
        assert post_id
        if user_token:
            assert check_user_token_valid(user_token)
            user = get_user_by_token(user_token)
            posts = get_posts_for_user(user)
        else:
            user = None
            posts = get_posts_default()
        post_index = list(posts).index(Post.objects.get(pk=int(post_id)))
        posts = posts[post_index + 1:post_index + AJAX_MAX_POSTS + 1]
        data = []
        for post in posts:
            item = {
                'id': post.id,
                'author_id': post.author.id,
                'author_username': post.author.username,
                'creation_date': post.creation_date.strftime('%d:%m:%Y:%H:%M:%S'),
                'has_login': True if user else False,
                'post_liked': bool(post.like_set.filter(user=user)),
                'post_likes': len(post.like_set.all()),
                'post_comms': len(post.comment_set.all()),
                'title': post.title,
                'content': post.content,
            }
            data.append(item)
        return JsonResponse({'data': data})
    except (AssertionError, ObjectDoesNotExist):
        return HttpResponseForbidden()


def ajax_like(request):
    try:
        assert is_ajax(request), 'not ajax'
        assert request.method == 'POST', 'not post'
        token = request.POST.get('token')
        post_id = request.POST.get('post_id')
        method = request.POST.get('method')
        assert all([i is not None for i in [token, post_id, method]]), "data wrong"
        assert method in ['add', 'remove'], 'method wrong'
        assert check_user_token_valid(token), 'token fail'

        user = get_user_by_token(token)
        post = Post.objects.get(pk=post_id)
        if method == 'add':
            if not Like.objects.filter(post=post).filter(user=user).exists():
                Like.objects.create(
                    post=post,
                    user=user
                )
        elif method == 'remove':
            _prev = Like.objects.filter(post=post).filter(user=user).first()
            if _prev:
                _prev.delete()

        likes = len(post.like_set.all())
        return JsonResponse({
            'message': 'OK',
            'likes': likes
        })
    except (AssertionError, ObjectDoesNotExist) as e:
        print(e)
        return HttpResponseForbidden()