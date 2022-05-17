from django.urls import path, reverse
from django.http import HttpResponseRedirect

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('login/', login, name='login'),
    path(r'', to_login, name='home'),
]

if DEBUG:
    urlpatterns = [

    ] + urlpatterns
