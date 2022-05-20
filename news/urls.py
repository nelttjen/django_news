from django.urls import path

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('', index),
    path('test/', test),
]

if DEBUG:
    urlpatterns = [

    ] + urlpatterns
