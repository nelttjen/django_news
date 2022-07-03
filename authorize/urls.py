from django.urls import path, reverse, re_path

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('login/', def_login, name='login'),
    path('register/', def_register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('activate/<str:key>/', activate, name='activate'),
    path('forgot/', forgot_password, name='forgot'),
    path('reset/', reset_password, name='reset'),


    path('to_profile/', to_profile, name='to_profile'),
    path('', to_login, name='home'),

]

if DEBUG:
    urlpatterns = [
        path('debug/', test_func, name='debug')
    ] + urlpatterns
