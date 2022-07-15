from django.urls import path, re_path

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('', index),
    path('test/', test),
    path('new_post/', new_post),
    path('my_posts/', my_posts),
    re_path(r'^my_posts/edit/id(?P<post_id>\d+)$', edit_post)
]

if DEBUG:
    urlpatterns = [
        path('show/', show, name='show'),
    ] + urlpatterns
