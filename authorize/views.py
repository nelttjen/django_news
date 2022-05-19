from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect as redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from news_django.settings import MESSAGES_CLASSES
from .forms import *

# Create your views here.


def to_login(request):
    return redirect('/auth/login')


def def_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data.get('login'), password=data.get('password'))
            user2 = None
            if '@' in data.get('login'):
                email_user = User.objects.filter(email=data.get('login')).first()
                if email_user is not None:
                    user2 = authenticate(request, username=email_user.username,
                                         password=data.get('password'))
            if user is not None or user2 is not None:
                login(request, user if user is not None else user2)
                messages.success(request, 'Вы вошли в аккаунт')
                return redirect('/auth/profile')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Введите логин и пароль')
    else:
        form = LoginForm()
    data = {
        'form': form,
    }
    return render(request, 'authorize/login.html', context=data)


def def_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
    else:
        form = RegisterForm()
    data = {
        'form': form,
    }
    return render(request, 'authorize/register.html', context=data)
