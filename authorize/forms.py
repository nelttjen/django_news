from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from authorize.models import ResetPasswordCode, PreviousPassword


class LoginForm(forms.Form):
    login = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль')
    remember = forms.BooleanField(label='Запомнить меня', initial=True, required=False)


class RegisterForm(forms.Form):
    login = forms.CharField(label='Логин')
    email = forms.EmailField(label='Email')
    pass1 = forms.CharField(label='Пароль')
    pass2 = forms.CharField(label='Повторите пароль')
    rule_accepted = forms.BooleanField()


class ForgotForm(forms.Form):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    def check_login(self):
        login = self.cleaned_data.get('username')
        user = User.objects.filter(Q(username=login) | Q(email=login)).first()
        if user and user.is_active:
            return user
        return None


class ResetForm(forms.Form):
    pass1 = forms.CharField(label='Новый пароль', widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'password'}))
    pass2 = forms.CharField(label='Повторите пароль', widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'password'}))

    def check(self, key):
        db_code = ResetPasswordCode.objects.filter(Q(code=key) & Q(activated=False)).first()
        if db_code:
            if db_code.valid_until > timezone.now():
                return True
            else:
                db_code.delete()
        return False

    def get_user(self, key):
        return ResetPasswordCode.objects.filter(code=key).first().user

    def check_same(self):
        return self.cleaned_data.get('pass1') == self.cleaned_data.get('pass2')

    def set_password(self, key, user: User):
        # activate code and save prev password
        code = ResetPasswordCode.objects.filter(code=key).first()
        code.activated = True
        code.activated_on = timezone.now()
        code.previous_password = PreviousPassword.objects.create(
            user=user,
            password=user.password
        )
        code.save()

        # update user password
        user.password = make_password(self.cleaned_data.get('pass1'))
        user.save()