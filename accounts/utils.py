import random
from django.core.mail import send_mail
from .models import User, OTP
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_otp():
    return ''.join(random.choices('0123456789', k=6))


def send_otp(email):
    subject = "One time passcode Email Verification"
    otp_code = generate_otp()
    print(otp_code)
    user = User.objects.filter(email=email).first()
    if user:
        current_site = "smart_restaurant"
        message = (f"{user.first_name}, thank you for signing up on {current_site}."
                   f"Please verify your email with the OTP: {otp_code}")
        from_email = settings.EMAIL_HOST_USER

        OTP.objects.create(user=user, code=otp_code)

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email],
            )
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}")
    else:
        logger.error(f"No user found with email: {email}")


def send_normal_email(data):
    try:
        send_mail(
            subject=data['subject'],
            message=data['message'],
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[data['to']],
        )
    except Exception as e:
        logger.error(f"Failed to send OTP email to {data['to']}: {e}")
