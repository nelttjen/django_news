import string

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.sessions.models import Session
from django.utils import timezone

from .models import ActivatedUser, PreviousPassword


class LoginAbility(object):
    OK = 0
    TEMPBAN = 1
    BAN = 2

    @classmethod
    def check_user(cls, request, user: ActivatedUser, send_messages=True):
        if user.user.is_superuser:
            return cls.OK
        if user.is_banned:
            if user.banned_until > timezone.now():
                if send_messages:
                    date = user.banned_until.strftime('%d.%m.%Y')
                    time = user.banned_until.strftime('%H:%M:%S')
                    _f = f' администратором {user.banned_by_username}' if user.banned_by_username else ''
                    messages.error(request, f'Ваш аккаунт временно заблокирован{_f}!')

                    messages.error(request, f'Вы не можете войти в систему до')
                    messages.error(request, f'{date} {time} {timezone.get_current_timezone()}')
                    if user.banned_message:
                        messages.error(request, f'Сообщение администратора:')
                        messages.error(request, user.banned_message)
                return cls.TEMPBAN
            else:
                user.is_banned = False
                user.banned_until = None
                if not user.is_permanent_banned:
                    user.banned_on = None
                    user.banned_message = ''
                    user.banned_by_username = ''
                user.save()
        if user.is_permanent_banned:
            if send_messages:
                _f = f' администратором {user.banned_by_username}' if user.banned_by_username else ''
                messages.error(request, f'Ваш аккаунт перманентно заблокирован{_f}!')
                messages.error(request, 'Вы больше не сможете войти в систему')
                if user.banned_message:
                    messages.error(request, f'Сообщение администратора:')
                    messages.error(request, user.banned_message)
            return cls.BAN
        return cls.OK

    @classmethod
    def logout_user(cls, user: User):
        [s.delete() for s in Session.objects.all() if int(s.get_decoded().get('_auth_user_id')) == user.id]


class PasswordStrongCheck(object):

    PASS_MIN = 8
    PASS_MAX = 50
    PASS_SYMBOLS = '$%#_-+=!@'

    @classmethod
    def strong_check(cls, password) -> bool:
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

    @classmethod
    def password_test(cls, request, password, username='', _min=PASS_MIN, _max=PASS_MAX, _symbols=PASS_SYMBOLS,
                      send_messages=True, is_admin_messages=False, modeladmin=None) -> bool:
        allow_pass = string.ascii_letters + string.digits + _symbols

        def send(msg):
            if not is_admin_messages:
                messages.error(request, msg)
            else:
                modeladmin.message_user(request, msg, messages.ERROR)

        if not _min <= len(password) <= _max:
            if send_messages:
                message = f'Пароль должен быть от {_min} до {_max} символов'
                send(message)
            return False
        elif not all([i in allow_pass for i in password]):
            if send_messages:
                _format = f"и символы: {_symbols}" if _symbols else ''
                message = f'''Пароль может содержать только буквы латинского алфавита {_format}'''
                send(message)
            return False
        elif password == username:
            if send_messages:
                message = 'Логин и пароль не должны совпадать'
                send(message)
            return False
        elif not PasswordStrongCheck.strong_check(password):
            if send_messages:
                message = 'Пароль должен содержать хотя бы одну заглавную и строчную букву и одну цифру'
                send(message)
            return False
        return True
