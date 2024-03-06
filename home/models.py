from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
# Create your models here.
class Address(BaseModel):
    name = models.CharField(max_length = 200,default = 'New name')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    landmark = models.CharField(max_length = 500,default = 'something')
    

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

    class Meta:
        verbose_name_plural = 'Addresses'



class UserAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_addresses')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'User Addresses'


class Banner(BaseModel):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners')
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title