from django.db import models
from django.contrib.auth.models import User


# Create your models here.
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateField(default=timezone.now)
    last_edit_time = models.DateTimeField(default=timezone.now)
    is_posted = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()

    is_visible = models.BooleanField(default=True)


class Tag(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
