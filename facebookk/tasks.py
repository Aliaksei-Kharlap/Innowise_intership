from django.core.mail import send_mail

from facebookk.models import Page
from mysite import settings
from myuser.models import User
from mysite.celery import app


@app.task
def send(page_id):
    page = Page.objects.get(pk=page_id)
    users = page.followers.all()
    send_mail(
        f'New post from {page.name}',
        'Do not forget to like',
        settings.EMAIL_HOST_USER,
        [user.email for user in users],
        fail_silently=False
        )
