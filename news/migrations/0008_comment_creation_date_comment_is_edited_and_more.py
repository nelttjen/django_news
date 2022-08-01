# Generated by Django 4.0.4 on 2022-08-01 14:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_alter_pagetoken_expired'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='read',
            name='read_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.comment'),
        ),
        migrations.AlterField(
            model_name='commentlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_like_user', to='news.comment'),
        ),
    ]