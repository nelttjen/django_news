from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    city = models.CharField(max_length=250, default='')
    company = models.CharField(max_length=250, default='')
    websites = models.CharField(max_length=1000, default='')
    mobile = models.CharField(max_length=50, default='')
    balance = models.FloatField(default=0.0)
    total_gained = models.FloatField(default=0.0)
    total_withdraw = models.FloatField(default=0.0)
