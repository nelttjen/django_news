from django.urls import path, reverse, re_path

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('login/', def_login, name='login'),
    path('register/', def_register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('activate/<str:key>/', activate, name='activate'),

    path(r'', to_login, name='home'),

]

if DEBUG:
    urlpatterns = [

    ] + urlpatterns
