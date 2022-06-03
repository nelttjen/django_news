import string

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import UploadedFile

from news_django.settings import MAX_FILESIZE
from user_profile.models import ExtendedUser
from authorize.checks import PasswordStrongCheck

# used for password history
from authorize.models import PreviousPassword


class ImageForm(forms.Form):
    OK = 0
    SIZE = 1
    ERROR = 2

    file = forms.ImageField()

    def check_and_save(self, file: UploadedFile, user: User) -> int:
        if file.size > MAX_FILESIZE:
            return self.SIZE
        try:
            DEST = f'user_profile/static/user_profile/img/profile_images/{user.id}.png'
            with open(DEST, 'wb+') as img:
                for chunk in file.chunks():
                    img.write(chunk)
            return self.OK
        except Exception as e:
            return self.ERROR


class UserInfoForm(forms.Form):
    city = forms.CharField(label='Город', required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Введите город'}))
    company = forms.CharField(label='Компания', required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Название компании'}))
    website = forms.CharField(label='Сайт', required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Ваш сайт'}))
    mobile = forms.CharField(label='Телефон', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel',
                                                           'pattern': '[+]{1}[0-9]{11,14}',
                                                           'placeholder': 'Введите номер телефона'}))

    # def from_user(self, user: ExtendedUser):
    #     self.city.initial = user.city
    #     self.company.initial = user.company
    #     self.website.initial = user.websites
    #     self.mobile.initial = user.mobile


class ChangePasswordForm(forms.Form):
    OLD = 1
    SAME = 2
    STRONG = 3
    NOT_EQUALS = 4
    MIN_MAX = 5
    SYMBOLS = 6
    LOG_PASS = 7
    OK = 0

    PASS_MIN = 8
    PASS_MAX = 50

    INPUT_TYPE = 'text'

    old_pass = forms.CharField(label='Текущий пароль',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password',
                                                             'placeholder': 'Текущий пароль'}))
    new_pass1 = forms.CharField(label='Новый пароль',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'type': INPUT_TYPE,
                                                              'placeholder': 'Новый пароль'}))
    new_pass2 = forms.CharField(label='Повторите пароль',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'type': INPUT_TYPE,
                                                              'placeholder': 'Поторите пароль'}))

    def check(self, user: User) -> int:
        c_data = self.cleaned_data
        o_pass = c_data.get('old_pass')
        pass1 = c_data.get('new_pass1')
        pass2 = c_data.get('new_pass2')

        allow_pass = string.ascii_letters + string.digits + '$%#_-+=!@'

        if not self.PASS_MIN <= len(pass1) <= self.PASS_MAX:
            return self.MIN_MAX
        elif pass1 != pass2:
            return self.NOT_EQUALS
        elif pass1 == user.username:
            return self.LOG_PASS
        elif not all([i in allow_pass for i in pass1]):
            return self.SYMBOLS
        elif not PasswordStrongCheck.strong_check(pass1):
            return self.STRONG
        elif not check_password(o_pass, user.password):
            return self.OLD
        elif pass1 == o_pass:
            return self.SAME
        return self.OK

    def set(self, user: User):
        # test: ZXCZXCzxc123

        # Non-profile action!
        PreviousPassword.objects.create(
            user=user,
            password=user.password,
        )

        user.set_password(self.cleaned_data.get('new_pass1'))
        user.save()


