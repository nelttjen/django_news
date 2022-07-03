from django.urls import path

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('', index),
    path('test/', test),
    path('new_post/', new_post)
]

if DEBUG:
    urlpatterns = [
        path('snow/', show, name='show'),
        path('date/', time)
    ] + urlpatterns
