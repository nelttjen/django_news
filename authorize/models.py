import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ActivatedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    verification_code = models.CharField(max_length=200, unique=True)
    activated = models.BooleanField(default=False)
    valid_until = models.DateTimeField(default=(timezone.now() + datetime.timedelta(seconds=60 * 30)))
