import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


DEFAULT_CODE_TIME = timezone.now() + datetime.timedelta(seconds=60 * 30)  # 30 mins


class ActivatedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    verification_code = models.CharField(max_length=200, unique=True)
    activated = models.BooleanField(default=False)
    valid_until = models.DateTimeField(default=DEFAULT_CODE_TIME)


class PreviousPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)

    changed_on = models.DateTimeField(default=timezone.now)
    password = models.CharField(max_length=200)


class ResetPasswordCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)

    code = models.CharField(max_length=200, unique=True)
    valid_until = models.DateTimeField(default=DEFAULT_CODE_TIME)

    activated = models.BooleanField(default=False)
    activated_on = models.DateTimeField(blank=True, null=True)
    previous_password = models.OneToOneField(PreviousPassword, on_delete=models.CASCADE, blank=True, null=True)