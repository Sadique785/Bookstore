from django.conf import settings
from django.core.mail import send_mail
import random, string


def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp


def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email,recipient_list)





def send_account_activation_email(email, email_token):
    subject = "Your account need to be verified"
    email_from = settings.EMAIL_HOST_USER
    activation_url = f"{settings.EMAIL_VERIFICATION_URL}/{email_token}"
    message = f"Hi, click on the link to activate your account {activation_url}"
    

    send_mail(subject, message, email_from, [email])
    


