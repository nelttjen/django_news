# Generated by Django 4.0.4 on 2022-07-20 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorize', '0002_alter_activateduser_code_valid_until_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='previouspassword',
            name='changed_on',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
