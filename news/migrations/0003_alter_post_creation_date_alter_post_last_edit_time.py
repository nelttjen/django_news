# Generated by Django 4.0.4 on 2022-06-30 22:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_alter_post_creation_date_alter_post_last_edit_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='creation_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='post',
            name='last_edit_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
