from __future__ import annotations

import datetime
import hashlib
import random
import string
from smtplib import SMTPSenderRefused, SMTPAuthenticationError

from django.contrib.auth.decorators import user_passes_test
from django.db.models import ObjectDoesNotExist, Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect as redirect
from django.db.utils import IntegrityError
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from .forms import RegisterForm, LoginForm, ForgotForm, ResetForm
from .models import ActivatedUser, ResetPasswordCode, DEFAULT_CODE_TIME
from .checks import LoginAbility, PasswordStrongCheck
from news_django.settings import DOMAIN_NAME, EMAIL_HOST_USER, DEBUG, SESSION_EXPIRY
from user_profile.models import ExtendedUser

# initial values
NICK_SYMBOLS = '_'

LOGIN_MIN = 4
LOGIN_MAX = 32


# not view defs
def send_email(data, silent_fail: bool = False) -> int:
    try:
        assert all([data.get('subject'), data.get('plain_message'), EMAIL_HOST_USER, data.get('email_to')])
        if data.get('html_message'):
            return send_mail(
                data.get('subject'),
                data.get('plain_message'),
                EMAIL_HOST_USER,
                data.get('email_to'),
                html_message=data.get('html_message'),
                fail_silently=silent_fail or not DEBUG
            )
        return send_mail(
            data.get('subject'),
            data.get('plain_message'),
            EMAIL_HOST_USER,
            data.get('email_to'),
            fail_silently=silent_fail or not DEBUG
        )
    except AssertionError:
        return 0


def md5code(username=''):
    return hashlib.md5((timezone.now().__str__() +
                        username +
                        str(random.randint(0, 999999))).encode())


def create_code(user, deactivate_user: bool = False, delete_user: bool = False) -> bool:
    code = md5code(user.username)
    valid_until = timezone.now() + datetime.timedelta(seconds=60 * DEFAULT_CODE_TIME)
    a_user = ActivatedUser.objects.create(
        user=user,
        activated=False,
        verification_code=code.hexdigest(),
        code_valid_until=valid_until,
    )
    if not user.is_superuser:
        subject = 'Активация нового аккаунта'
        link = f'{DOMAIN_NAME}/auth/activate/{code.hexdigest()}'
        html_message = render_to_string('authorize/mail/register.html', context={
            'username': user.username,
            'link': link,
            'time': DEFAULT_CODE_TIME,
         })
        plain_message = strip_tags(html_message)
        email_data = {
            'subject': subject,
            'plain_message': plain_message,
            'email_to': [user.email],
            'html_message': html_message,
        }
        try:
            if not send_email(email_data):
                if deactivate_user:
                    user.is_active = False
                elif delete_user:
                    user.delete()
                return False
        except (SMTPSenderRefused, SMTPAuthenticationError) as e:
            if delete_user:
                user.delete()
            raise e
    else:
        # superuser activation bypass
        a_user.activated = True
        a_user.save()
    return True


def create_reset_code(user: User):
    already = ResetPasswordCode.objects.filter(Q(user=user) & Q(activated=False)).first()
    if already:
        if already.code_valid_until > timezone.now():
            return None
        else:
            already.delete()
    return ResetPasswordCode.objects.create(
        code=md5code(user.username).hexdigest(),
        activated=False,
        user=user,
        valid_until=timezone.now() + datetime.timedelta(seconds=60 * DEFAULT_CODE_TIME),
    )


def to_login(request):
    return redirect('/auth/login')


def to_profile(request):
    # remove ?next from url
    return redirect('/profile')


def no_login(user: User) -> bool:
    return not user.is_authenticated


def create_new_user(data) -> User:
    _new = User.objects.create_user(
        username=data.get('login'),
        email=data.get('email'),
        password=data.get('pass1'),
    )
    ExtendedUser.objects.create(
        user=_new
    )
    return _new


def register_test(request, data) -> bool:
    allow_nick = string.ascii_letters + string.digits + NICK_SYMBOLS

    _login = data.get('login')
    _pass1 = data.get('pass1')
    _pass2 = data.get('pass2')

    if not LOGIN_MIN <= len(_login) <= LOGIN_MAX:
        messages.error(request, f'Длинна логина должна быть от {LOGIN_MIN} до {LOGIN_MAX} символов')
        return False
    elif not all([i in allow_nick for i in _login]):
        messages.error(request, f'Логин может содержать только буквы латинского алфавита и символы: {NICK_SYMBOLS}')
        return False
    elif _pass1 != _pass2:
        messages.error(request, 'Пароли не совпадают')
        return False
    return PasswordStrongCheck.password_test(request, _pass1, _login)


# view defs

def test_func(request):
    # debug code here

    return HttpResponse('ok')


# no_login will restrict access to already signed up users
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
                # if somehow it won`t be created
                try:
                    activated = user.activateduser.activated
                except ObjectDoesNotExist:
                    create_code(user, deactivate_user=False)

                    # if superuser it`ll be bypassed activation in create_code func,
                    # so we need to login it next step as well
                    activated = user.is_superuser
                if activated:
                    # Need to check for any bans
                    if LoginAbility.check_user(request, user.activateduser) != LoginAbility.OK:
                        return redirect('/auth/login')

                    login(request, user)
                    if not data.get('remember'):
                        request.session.set_expiry(SESSION_EXPIRY)
                    if 'next' in request.GET.keys():
                        return redirect(request.GET.get('next'))
                    messages.success(request, 'Вы вошли в аккаунт')
                    return redirect('/profile')
                else:
                    # If account wasn`t activated via email
                    messages.info(request, 'На email, указанный при регистрации, '
                                           'было отправленно письмо для активации аккаунта.\n'
                                           'Письмо могло попасть в папку "Спам"')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Введите логин и пароль')
    else:
        form = LoginForm()
    return render(request, 'authorize/login.html', context={'form': form, })


@user_passes_test(no_login, login_url='/auth/to_profile')
def def_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if register_test(request, data):
                class EmailIntegrityError(Exception):
                    pass

                try:
                    if User.objects.filter(email=data.get('email')).first():
                        raise EmailIntegrityError
                    _new = create_new_user(data)
                    if create_code(_new, deactivate_user=False, delete_user=False):
                        messages.success(request, 'Регистрация успешна! '
                                                  'На ваш email была отправлена ссылка для активации аккаунта.')
                        return redirect('/auth/login')
                    else:
                        messages.error(request, 'Что-то пошло не так. Попробуйте ещё раз.')
                    return redirect('/auth/register')
                except IntegrityError:
                    messages.error(request, 'Логин уже занят')
                except EmailIntegrityError:
                    messages.error(request, 'Email уже занят')
        else:
            messages.error(request, 'Заполните все поля и прочитайте правила')
    else:
        form = RegisterForm()

    data = {
        'form': form,
    }
    return render(request, 'authorize/register.html', context=data)


def activate(request, key):
    a_user = ActivatedUser.objects.filter(verification_code=key).first()
    if a_user and not a_user.activated:
        if not timezone.now() < a_user.code_valid_until:
            user = a_user.user
            a_user.delete()
            create_code(user)
            return HttpResponse('link expired. new link was sent to your email')
        a_user.activated = True
        a_user.activated_on = timezone.now()
        a_user.save()
        messages.success(request, 'account activated. Now you can log in into your account')
        return redirect('/auth/login')
    return HttpResponse('Invalid activation code or link has expired')


@user_passes_test(no_login, login_url='/auth/to_profile')
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotForm(request.POST)
        if form.is_valid():
            user = form.check_login()
            msg = False
            if user:
                code = create_reset_code(user)
                if code:
                    data = {
                        'subject': 'Восстановление пароля',
                        'message': f'Ваша ссылка для восстановления пароля: '
                                   f'{DOMAIN_NAME}/auth/reset?key={code.code}\n'
                                   f'Ссылка действительна в течении 30 минут',
                        'email_to': [user.email]
                    }
                    send_email(data)
                else:
                    messages.info(request, f'На ваш email уже был отправлен код для восстановления пароля')
                    msg = True
            if not msg:
                messages.info(request, f'На email, указанный при регистрации было отправленно письмо '
                                       f'с ссылкой для восстановления аккаунта. Если вы не получили письмо, '
                                       f'возможно пользователя не существует или он был заблокирован')
    else:
        form = ForgotForm()
    return render(request, 'authorize/forgot.html', context={'form': form})


@user_passes_test(no_login, login_url='/auth/to_profile')
def reset_password(request):
    form = ResetForm()
    key = request.GET.get('key')
    if request.method == 'POST':
        form = ResetForm(request.POST)
        if form.is_valid():
            if not form.check(key):
                messages.error(request, 'Что-то пошло не так. Возможно истек срок дейстия кода или он не существует')
                return redirect('/auth/login')
            f_data = form.cleaned_data
            user = form.get_user(key)
            if not form.check_same():
                messages.error(request, 'Пароли не совпадают')
            elif PasswordStrongCheck.password_test(request, f_data.get('pass1'), user.username):
                form.set_password(key, user)
                messages.success(request, 'Пароль изменен. Теперь вы можете войти в аккаунт с новым паролем')
                return redirect('/auth/login')
    elif request.method == 'GET':
        if not form.check(key):
            form = None
    return render(request, 'authorize/reset.html', context={'form': form})


def logout_user(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    response = redirect('/auth/login')
    if request.COOKIES.get('user_token') is not None:
        response.delete_cookie('user_token')
    return response
