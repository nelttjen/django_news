from __future__ import annotations

import asyncio
import datetime
import hashlib
import os
import random
import string

from django.contrib.auth.decorators import user_passes_test
from django.db.models import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect as redirect
from django.db.utils import IntegrityError
from django.core.mail import send_mail
from django.utils import timezone

from .forms import *
from .models import ActivatedUser
from news_django.settings import env, DOMAIN_NAME, EMAIL_HOST_USER, DEBUG
from user_profile.models import ExtendedUser


def send_email(data) -> int:
    try:
        assert all([data.get('subject'), data.get('message'), EMAIL_HOST_USER, data.get('email_to')])
        return send_mail(
            data.get('subject'),
            data.get('message'),
            EMAIL_HOST_USER,
            data.get('email_to'),
            fail_silently=not DEBUG
        )
    except AssertionError:
        return 0


def create_code(user) -> bool:
    code = hashlib.md5((timezone.now().__str__() +
                        user.username +
                        str(random.randint(0, 999999))).encode())
    a_user = ActivatedUser.objects.create(
        user=user,
        activated=False,
        verification_code=code.hexdigest()
    )
    if not user.is_superuser:
        email_data = {
            'subject': 'Активация нового аккаунта.',
            'message': f'Ваша ссылка для активации аккаунта: {DOMAIN_NAME}/auth/activate/{code.hexdigest()}\n'
                       f'Ссылка действительна 30 минут.',
            'email_to': [user.email],
        }
        if not send_email(email_data):
            user.is_active = False
            return False
    else:
        a_user.activated = True
        a_user.save()
    return True


def activate(request, key):
    a_user = ActivatedUser.objects.filter(verification_code=key).first()
    if a_user and not a_user.activated:
        if not timezone.now() < a_user.valid_until:
            user = a_user.user
            a_user.delete()
            create_code(user)
            return HttpResponse('link expired. new link was sent to your email')
        a_user.activated = True
        a_user.save()
        messages.success(request, 'account activated. Now you can log in into your account')
        return redirect('/auth/login')
    return HttpResponse('Invalid activation code or link has expired')


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

def to_login(request):
    return redirect('/auth/login')


def to_profile(request):
    return redirect('/profile')


def no_login(user: User):
    return not user.is_authenticated


@user_passes_test(no_login, login_url='/auth/to_profile')
def def_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data.get('login'), password=data.get('password'))
            if '@' in data.get('login'):
                email_user = User.objects.filter(email=data.get('login')).first()
                if email_user is not None:
                    user = authenticate(request, username=email_user.username,
                                        password=data.get('password'))
            if user is not None:
                try:
                    activated = user.activateduser.activated
                except ObjectDoesNotExist:
                    create_code(user)
                    activated = user.is_superuser
                if activated:
                    login(request, user)
                    if not data.get('remember'):
                        request.session.set_expiry(30 * 60)  # 30 mins
                    messages.success(request, 'Вы вошли в аккаунт')
                    return redirect('/profile')
                else:
                    messages.info(request, 'На email, указанный при регистрации, '
                                           'было отправленно письмо для активации аккаунта.\n'
                                           'Письмо могло попасть в папку "Спам"')
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


@user_passes_test(no_login, login_url='/auth/to_profile')
def def_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            allow_nick = string.ascii_letters + string.digits + '_'
            allow_pass = string.ascii_letters + string.digits + '$%#_-+=!@'

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
                    _new = User.objects.create_user(
                        username=data.get('login'),
                        email=data.get('email'),
                        password=data.get('pass1'),
                    )
                    ExtendedUser.objects.create(
                        user=_new
                    )
                    if create_code(_new):
                        messages.success(request, 'Регистрация успешна! '
                                                  'На ваш email была отправлена ссылка для активации аккаунта.')
                    else:
                        messages.error(request, 'Что-то пошло не так. Попробуйте ещё раз.')
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
