from django.urls import path, re_path

from .views import *


urlpatterns = [
    re_path('likes/(?P<post_id>\d+)$', LikesView.as_view())
]
