from django.db import models
from django.contrib.auth.models import User

DEFAULT_CODE_TIME = 30  # 30 mins


class ActivatedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    verification_code = models.CharField(max_length=200, unique=True)
    code_valid_until = models.DateTimeField()

    activated = models.BooleanField(default=False)
    activated_on = models.DateTimeField(blank=True, null=True)

    is_banned = models.BooleanField(default=False)
    is_permanent_banned = models.BooleanField(default=False)
    banned_on = models.DateTimeField(blank=True, null=True)
    banned_until = models.DateTimeField(blank=True, null=True)
    banned_message = models.CharField(max_length=500, blank=True)
    banned_by_username = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.user.username} ({self.activated})'


class PreviousPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)

    changed_on = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=200)

    def __str__(self):
        return f'[{self.id}] ({self.changed_on}) {self.user.username}'


class ResetPasswordCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)

    code = models.CharField(max_length=200, unique=True)
    valid_until = models.DateTimeField()

    activated = models.BooleanField(default=False)
    activated_on = models.DateTimeField(blank=True, null=True)
    previous_password = models.OneToOneField(PreviousPassword, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'[{self.id}] ({self.user.username}) Reset Password code'