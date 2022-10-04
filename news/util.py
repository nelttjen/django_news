import datetime
import uuid

from django.contrib.auth.models import User
from django.utils import timezone

from news.models import PageToken, Post


# global vars
LATEST_MAX_POSTS = 8
LIKED_MAX_POSTS = 8
MAIN_MAX_POSTS = 1
AJAX_MAX_POSTS = 25


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_user_by_token(token):
    token_obj = PageToken.objects.filter(token=token).first()
    if not token_obj:
        return False
    return token_obj.user


def check_user_token_valid(token):
    token_obj = PageToken.objects.filter(token=token).first()
    if not token_obj:
        return False
    return token_obj.expired > timezone.now()


def user_token(user):
    if not isinstance(user, User):
        return None
    _prev = PageToken.objects.filter(user=user).first()
    if _prev:
        if not check_user_token_valid(_prev.token):
            _prev.delete()
        else:
            return _prev
    return PageToken.objects.create(
        token=uuid.uuid4().hex,
        user=user,
        expired=timezone.now() + datetime.timedelta(days=1)
    )


def get_posts_for_user(user):
    now = timezone.now()
    days_30 = now - datetime.timedelta(days=90)
    return Post.objects.filter(
        is_posted=True
    ).filter(
        creation_date__range=[days_30, now]
    ).all()


def get_posts_default():
    now = timezone.now()
    days_30 = now - datetime.timedelta(days=90)
    return Post.objects.filter(
        is_posted=True
    ).filter(
        creation_date__range=[days_30, now]
    ).all()


def check_cookie(request, response, token):
    if request.COOKIES.get('user_token'):
        if not check_user_token_valid(request.COOKIES.get('user_token')) and token:
            response.set_cookie("user_token", token.token)
    elif token:
        response.set_cookie("user_token", token.token)