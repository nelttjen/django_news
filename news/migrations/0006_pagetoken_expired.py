# Generated by Django 4.0.4 on 2022-07-28 04:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_pagetoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagetoken',
            name='expired',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
