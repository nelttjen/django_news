# Generated by Django 4.0.4 on 2022-07-28 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_pagetoken_expired'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagetoken',
            name='expired',
            field=models.DateTimeField(),
        ),
    ]
