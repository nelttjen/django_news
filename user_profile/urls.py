from django.urls import path, reverse
from django.http import HttpResponseRedirect

from news_django.settings import DEBUG
from .views import *

urlpatterns = [
    # path(r'', def_profile, name='home'),

]

if DEBUG:
    urlpatterns = [

    ] + urlpatterns
