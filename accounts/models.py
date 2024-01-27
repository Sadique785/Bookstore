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
from products.models import Product , LanguageVariant, EditionVariant

# Create your models here.


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    is_email_verified = models.BooleanField(default = False)
    email_token = models.CharField(max_length = 100, null = True, blank = True)
    profile_image = models.ImageField(upload_to='profile')
    mobile = models.CharField(max_length=15, null=True, blank=True)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_valid_until = models.DateTimeField(null=True, blank=True)



    def get_cart_count(self):
        return CartItem.objects.filter(cart__is_paid = False, cart__user = self.user).count()



class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'carts')
    is_paid = models.BooleanField(default = False)
    
    def get_cart_total(self):
        cart_items = self.cart_item.all()
        total = 0

        for cart_item in cart_items:
            # Multiply each cart item's price by its quantity and add to the total
            total += cart_item.price

        return total


    # def get_cart_total(self):
    #     cart_items = self.cart_item.all()
    #     price = []
    #     for cart_item in cart_items:
    #         price.append(cart_item.product.price)
    #         if cart_item.edition_variant:
    #              edition_variant_price = cart_item.edition_variant.price
    #              price.append(edition_variant_price)
    #     return sum(price)



class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete = models.SET_NULL,null=True, related_name = 'cart_item')
    product = models.ForeignKey(Product, on_delete = models.SET_NULL,null=True)
    language_variant = models.ForeignKey(LanguageVariant, on_delete = models.SET_NULL,null=True)
    edition_variant = models.ForeignKey(EditionVariant, on_delete = models.SET_NULL,null=True)
    qty = models.IntegerField(default = 1)
    price = models.IntegerField(default = 0)


    


    def get_product_price(self):
        price = [self.product.price]

        if self.edition_variant:
            edition_variant_price = self.edition_variant.price
            price.append(edition_variant_price)

        if self.qty:
            count = self.qty
            new_sum = (sum(price)) * count
        return new_sum
    def get_product_intial_price(self):
        price = [self.product.price]

        if self.edition_variant:
            edition_variant_price = self.edition_variant.price
            price.append(edition_variant_price)

        return sum(price)
    

    def save(self, *args, **kwargs):
        price = self.get_product_price()
        self.price = price
        if self.price == 0:

            self.price = self.get_product_price()

        super(CartItem, self).save(*args, **kwargs)

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
        
        