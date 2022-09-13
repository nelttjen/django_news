import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


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
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now_add=True)
    is_posted = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-creation_date', 'title')


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='like_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comment_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)

    is_visible = models.BooleanField(default=True)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_like_user')


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber_user')
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
    notifications = models.BooleanField(default=False)


class Read(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='read_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    read_time = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('title',)

    def __str__(self):
        return self.title


class PageToken(models.Model):
    token = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="token_user")
    expired = models.DateTimeField()