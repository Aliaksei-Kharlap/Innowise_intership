# Generated by Django 4.1.1 on 2022-09-23 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myuser', '0003_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=80, unique=True),
        ),
    ]