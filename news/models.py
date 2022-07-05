import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
from django.utils import timezone


def path_and_rename(instance, filename):
    upload_to = f'posts/{timezone.now().strftime("%Y/%m/%d/")}'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now=True)
    last_edit_time = models.DateTimeField(auto_now=True)
    is_posted = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-creation_date', '-last_edit_time', 'title')


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()

    is_visible = models.BooleanField(default=True)


class Read(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Tag(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
