from django.urls import path, re_path

from news_django.settings import DEBUG
from .views import *
from .api import *


ajax = [
    path('api/news', ajax_load_more_news, name='ajax_load_news'),
    path('api/like', ajax_like, name="ajax_like"),
]

urlpatterns = [
    path('', index),
    path('new_post/', new_post),
    path('my_posts/', my_posts),
    re_path(r'^my_posts/edit/id(?P<post_id>\d+)$', edit_post),
    re_path(r'^posts/id(?P<post_id>\d+)$', view_post)
] + ajax

if DEBUG:
    urlpatterns = [
        path('show/', show, name='show'),
        path('js/', js, name='js')
    ] + urlpatterns
