import string

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect as redirect
from django.db.utils import IntegrityError


from .forms import *
from .models import ExtendedUser

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
                if not data.get('remember'):
                    request.session.set_expiry(30 * 60)  # 30 mins
                messages.success(request, 'Вы вошли в аккаунт')
                return redirect('/profile')
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
        if form.is_valid():
            data = form.cleaned_data
            allow_nick = string.ascii_letters + string.digits + '_'
            allow_pass = string.ascii_letters + string.digits + '$%#_-+=!@'

            def strong_check(password):
                dig, let, big_let = [False] * 3
                for i in password:
                    if all([dig, let, big_let]):
                        break
                    if i in string.ascii_lowercase:
                        let = True
                    elif i in string.ascii_uppercase:
                        big_let = True
                    elif i in string.digits:
                        dig = True
                return all([dig, let, big_let])

            if not 4 <= len(data.get('login')) <= 32:
                messages.error(request, 'Длинна логина должна быть от 4 до 32 символов')
            elif not 8 <= len(data.get('pass1')) <= 50:
                messages.error(request, 'Пароль должен быть от 8 до 50 символов')
            elif not all([i in allow_nick for i in data.get('login')]):
                messages.error(request, 'Логин может содержать только буквы латинского алфавита и символ подчеркивания')
            elif not all([i in allow_pass for i in data.get('pass1')]):
                messages.error(request, 'Пароль может содержать только буквы латинского алфавита и символы $%#_-+=!@')
            elif data.get('login') == data.get('pass1'):
                messages.error(request, 'Логин и пароль не должны совпадать')
            elif not strong_check(data.get('pass1')):
                messages.error(request, 'Пароль должен содержать хотя бы одну заглавную и строчную букву и одну цифру')
            elif data.get('pass1') != data.get('pass2'):
                messages.error(request, 'Пароли не совпадают')
            else:
                try:
                    User.objects.create_user(
                        username=data.get('login'),
                        email=data.get('email'),
                        password=data.get('pass1'),
                    )
                    ExtendedUser.objects.create(
                        user=User.objects.filter(username=data.get('login')).first()
                    )
                    messages.success(request, 'Регистрация успешна!')
                    return redirect('/auth/login')
                except IntegrityError:
                    messages.error(request, 'Логин уже занят')
        else:
            messages.error(request, 'Заполните все поля и прочитайте правила')
    else:
        form = RegisterForm()
    data = {
        'form': form,
    }
    return render(request, 'authorize/register.html', context=data)


def logout_user(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('/auth/login')



