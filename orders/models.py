from django.db import models
from base.models import BaseModel
from products.models import Product
from django.contrib.auth.models import User
from payments.models import  PaymentMethod



class Order(BaseModel):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PROCESSING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active  = models.BooleanField(default = True)
    is_delivered  = models.BooleanField(default = False)
    is_paid = models.BooleanField(default = True)



    
    def __str__(self):
        return f"Order {self.uid} - Status: {self.order_status} - Total: ${self.total_amount}"
    
    # def save(self, *args, **kwargs):

    #     all_items_paid = all(item.is_paid for item in self.order_items.all())

    #     self.is_paid = all_items_paid

    #     super().save(*args, **kwargs)
    
    def get_order_status_choices():
        return Order.ORDER_STATUS_CHOICES
    
    def get_status_display(self):
        pass

    def calculate_total(self):
        total = sum(item.price for item in self.order_items.all())
        return total
    

    def to_dict(self):
        return {
            'id': self.uid,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    def calculate_revenue(self):
        return sum(price for price in self.total_amount)

    

    
class OrderItem(BaseModel):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
    ]
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PROCESSING)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_name = models.CharField(max_length=255)
    edition_variant = models.CharField(max_length=255, blank=True, null=True)
    language_variant = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='order_images', blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Individual address fields
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    street_address = models.TextField()
    mobile = models.CharField(max_length=20)
    is_active  = models.BooleanField(default = True)
    is_delivered  = models.BooleanField(default = False)
    is_paid = models.BooleanField(default = True)

    def get_order_item_status_choices():
        return OrderItem.ORDER_STATUS_CHOICES
    def get_total(self):
        return self.price * self.quantity
    
    

    
    
    def to_dict(self):

        return {
            'uid': self.uid,
            'qty': self.quantity,
            'image': str(self.image.url) if self.image else None,
            'product_name': self.product_name,
            'edition_variant': self.edition_variant,
            'get_total': str(self.get_total()),
            'quantity': self.quantity,
            'order_status': self.order_status,
        }
    
        

    def __str__(self):
        return f"OrderItem {self.uid} - Order {self.order.uid}, Product {self.product_name}, Variant {self.edition_variant}"


class OrderAddress(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order_address')
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    street_address = models.TextField()
    mobile = models.CharField(max_length=20)

    # Additional fields
    email = models.EmailField()
    is_billing_address = models.BooleanField(default=False)
    is_shipping_address = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default = False)
    is_delivered = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.name}'s Address"


class OrderPayment(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Additional fields 
    card_number = models.CharField(max_length=20, blank=True)
    expiration_date = models.DateField(blank=True, null=True)
    cvv = models.CharField(max_length=4, blank=True)

    def __str__(self):
        return f"Payment for Order {self.order.uid}"



class OrderProduct(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_variant = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='order_images', blank=True, null=True)

    def __str__(self):
        return f"OrderProduct {self.uid} - Order {self.order.uid}, Product {self.product_name}, Variant {self.product_variant}"
    


    # ... (Same as above)
