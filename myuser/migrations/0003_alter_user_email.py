# Generated by Django 4.1.1 on 2022-09-21 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myuser', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]