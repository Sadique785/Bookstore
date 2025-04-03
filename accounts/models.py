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
from products.models import Product , LanguageVariant, EditionVariant, Coupon
from orders.models import OrderItem

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
    coupon = models.ForeignKey(Coupon, on_delete = models.SET_NULL, null = True, blank = True)
    is_paid = models.BooleanField(default = False)
    razor_pay_order_id = models.CharField(max_length = 100, null = True, blank = True)
    razor_payment_id = models.CharField(max_length = 100, null = True, blank = True)
    razor_payment_signature = models.CharField(max_length = 100, null = True, blank = True)
    delivery_charge = models.IntegerField(null = True, blank = True, default = 59)
 
    
    def get_cart_total(self):
        cart_items = self.cart_item.filter(product__stock_quantity__gt = 0)
        total = 0

        for cart_item in cart_items:
            total += cart_item.price


        if self.coupon:
            if self.coupon.minimum_amount < total:
                return total - self.coupon.discount_price

        return total
    
    def get_cart_total_couponless(self):
        cart_items = self.cart_item.filter(product__stock_quantity__gt = 0)
        total = 0

        for cart_item in cart_items:
            total += cart_item.price


        

        return total
    
    def get_final_total(self):
        if self.get_cart_total() < 999:

            return self.get_cart_total() + self.delivery_charge
        else:
            return self.get_cart_total()


    


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete = models.SET_NULL,null=True, related_name = 'cart_item')
    product = models.ForeignKey(Product, on_delete = models.SET_NULL,null=True, related_name = 'product')
    language_variant = models.ForeignKey(LanguageVariant, on_delete = models.SET_NULL,null=True,related_name = 'language_variant')
    edition_variant = models.ForeignKey(EditionVariant, on_delete = models.SET_NULL,null=True,related_name = 'edition_variant')
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




class Wallet(BaseModel):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    balance = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00)
    refund = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0.00)


    def __str__(self):
        return f"{self.user.first_name}'s Wallet"
    



class Transaction(BaseModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    description = models.TextField(blank = True)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.timestamp}"



def generate_invoice_name():
    return f'INV{random.randint(100, 999)}'

class Invoice(models.Model):
    name = models.CharField(max_length=10, default=generate_invoice_name, unique=True)
    order_item = models.ForeignKey(OrderItem, on_delete = models.CASCADE)
    

    def __str__(self):
        return self.name









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
            
            

    except Exception as e:
        print(e) 









        
        