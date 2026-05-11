from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    subject = 'Bem-vindo ao Dimbo Tools!'
    html_message = render_to_string('accounts/emails/welcome.html', {'user': user})
    plain_message = f'Olá {user.username},\n\nBem-vindo ao Dimbo Tools. Comece já a usar as nossas ferramentas gratuitamente.\n\nAceda: {settings.SITE_URL}'
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_password_reset_email(user, reset_url):
    subject = 'Redefinição de palavra-passe - Dimbo Tools'
    html_message = render_to_string('accounts/emails/password_reset.html', {'user': user, 'reset_url': reset_url})
    plain_message = f'Olá {user.username},\n\nClique no link para redefinir a sua palavra-passe: {reset_url}'
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )