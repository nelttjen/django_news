from django.urls import path, reverse
from django.http import HttpResponseRedirect

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('login/', def_login, name='login'),
    path('profile/', to_login, name='profile'),
    path('register/', def_register, name='register'),

    path(r'', to_login, name='home'),

]

if DEBUG:
    urlpatterns = [

    ] + urlpatterns
