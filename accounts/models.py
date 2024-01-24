from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from django.core.mail import send_mail
import string
import random
from datetime import timedelta
from django.utils import timezone

# Create your models here.


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    is_email_verified = models.BooleanField(default = False)
    email_token = models.CharField(max_length = 100, null = True, blank = True)
    profile_image = models.ImageField(upload_to='profile')
    mobile = models.CharField(max_length=15, null=True, blank=True)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_valid_until = models.DateTimeField(null=True, blank=True)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         if not hasattr(instance, 'profile'):
#             Profile.objects.create(user=instance)

# def is_otp_valid(self):
#         return self.otp_valid_until > timezone.now() if self.otp_valid_until else False

@receiver(post_save, sender = User)
def send_email(sender, instance, created, **kwargs):
    try:
        if created:
            
            email_token = str(uuid.uuid4())


            Profile.objects.create(
                user=instance,
                email_token=email_token,
            )

            email = instance.email
            send_account_activation_email(email, email_token)
            
            # subject = 'Account Activation'
            # message = f'Your account activation token is: {email_token}'
            # from_email = 'vssadique785@gmail.com'  
            # to_email = [email]
            
            # # Send email
            # send_mail(subject, message, from_email, to_email)

    except Exception as e:
        print(e) 

# @receiver(post_save, sender=User)
# def send_otp(sender, instance, created, **kwargs):
#     try:
#         if created:
#             email = instance.email
#             email_token = str(uuid.uuid4())
#             otp_code = generate_otp()  

           
#             otp_validity_duration = timedelta(minutes=5)
#             otp_valid_until = timezone.now() + otp_validity_duration

          
#             Profile.objects.create(
#                 user=instance,
#                 email_token=email_token,
#                 otp_code=otp_code,
#                 otp_valid_until=otp_valid_until
#             )

          
#             send_otp_email(email, otp_code)
            
#     except Exception as e:
#         print(e)
        
        