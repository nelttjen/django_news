from django.urls import path

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('', index),
    path('test/', test),
    path('new_post/', new_post),
    path('my_posts/', my_posts),
]

if DEBUG:
    urlpatterns = [
        path('show/', show, name='show'),
        path('date/', time)
    ] + urlpatterns
