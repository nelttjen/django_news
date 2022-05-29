from django.urls import path, reverse
from django.http import HttpResponseRedirect

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    path('', def_profile, name='home'),
    path('edit/', profile_user_info, name='edit'),
    path('change_password/', profile_user_password, name='change-password')

]

if DEBUG:
    urlpatterns = [

    ] + urlpatterns
