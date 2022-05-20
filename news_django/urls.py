"""news_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from django.http import HttpResponseRedirect as redirect
from django.views.static import serve

from news.views import *
from news_django import settings
from news_django.settings import DEBUG


def to_news(r):
    return redirect('/news/')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('auth/', include('authorize.urls')),
    path('', to_news),
]


