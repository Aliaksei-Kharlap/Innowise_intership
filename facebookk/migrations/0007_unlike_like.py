# Generated by Django 4.1.1 on 2022-09-22 20:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('facebookk', '0006_alter_subscription_page_to_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uposts_to', to='facebookk.post')),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unlike_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lposts_to', to='facebookk.post')),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
