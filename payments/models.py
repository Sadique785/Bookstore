from django.db import models
# from orders.models import Order
from base.models import BaseModel

# Create your models here.



class PaymentMethod(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    


# class Payment(BaseModel):
#     PENDING = 'pending'
#     PAID = 'paid'
#     FAILED = 'failed'

#     PAYMENT_STATUS_CHOICES = [
#         (PENDING, 'Pending'),
#         (PAID, 'Paid'),
#         (FAILED, 'Failed'),
#         # Add more choices as needed
#     ]

#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name = 'payment_method')
#     order = models.ForeignKey(
#         to=Order,
#         on_delete=models.CASCADE,
#         related_name='order_payments',
#     )
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PENDING)


#     def __str__(self):
#         return f"Payment - Amount: {self.amount}, Method: {self.payment_method.name}"