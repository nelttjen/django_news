# Generated by Django 4.0.4 on 2022-06-01 22:11

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('authorize', '0007_alter_activateduser_valid_until_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activateduser',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AddField(
            model_name='activateduser',
            name='activated_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activateduser',
            name='banned_by_username',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='activateduser',
            name='banned_message',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='activateduser',
            name='banned_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activateduser',
            name='banned_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='activateduser',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activateduser',
            name='is_permanent_banned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='activateduser',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 1, 22, 41, 6, 646052, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='resetpasswordcode',
            name='previous_password',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authorize.previouspassword'),
        ),
        migrations.AlterField(
            model_name='resetpasswordcode',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 1, 22, 41, 6, 646052, tzinfo=utc)),
        ),
    ]
