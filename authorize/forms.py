from django.forms import Form, CharField, BooleanField, EmailField


class LoginForm(Form):
    login = CharField(label='Логин')
    password = CharField(label='Пароль')
    remember = BooleanField(label='Запомнить меня', initial=True)


class RegisterForm(Form):
    login = CharField(label='Логин')
    email = EmailField(label='Email')
    pass1 = CharField(label='Пароль')
    pass2 = CharField(label='Повторите пароль')