
# from datetime import timezone
from datetime import datetime
from django.utils import timezone 

from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
# Create your models here.


class Category(BaseModel):
    
    category_name = models.CharField(max_length = 100)
    slug = models.SlugField(unique = True, null = True, blank = True)
    category_image = models.ImageField(upload_to="categories")
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(default = 'Write something')
    is_listed = models.BooleanField(default = True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)


    def __str__(self) -> str:
        return self.category_name
    
class SubCategory(BaseModel):
    subcategory_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = 'category')
    sub_slug = models.SlugField(unique = True, blank = True)
    category_image = models.ImageField(upload_to="categories" )
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(default = 'Write something')
    


    def save(self, *args, **kwargs):
        self.sub_slug = slugify(self.subcategory_name)
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.subcategory_name
    




class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    # Add more fields as needed for author details

    def __str__(self):
        return self.name


class LanguageVariant(BaseModel):
    name = models.CharField(max_length = 100)
    price = models.IntegerField(default=0)
    stock_quantity = models.PositiveIntegerField(default = 0)

    def __str__(self) -> str:
        return self.name
    
class EditionVariant(BaseModel):
    name = models.CharField(max_length = 100)
    price = models.IntegerField(default=0)
    stock_quantity = models.PositiveIntegerField(default = 0)
    
    def __str__(self) -> str:
        return self.name


class Product(BaseModel):
    product_name = models.CharField(max_length = 100)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = 'products', null = True)
    sub_category = models.ForeignKey(SubCategory, on_delete = models.CASCADE, related_name = 'products', null = True)
    slug = models.SlugField(unique = True, null = True, blank = True)
    price = models.IntegerField(null = True)
    product_description = models.TextField()
    regular_price = models.IntegerField(null = True)
    promotional_price = models.IntegerField(null = True)
    currency = models.CharField(max_length = 5, null = True)
    tax_rate = models.IntegerField(null = True)
    has_audiobook = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_listed = models.BooleanField(default = True)
    is_category_listed = models.BooleanField(default = True)
    language_variant = models.ManyToManyField(LanguageVariant, blank=True)
    edition_variant = models.ManyToManyField(EditionVariant, blank=True)
    stock_quantity = models.PositiveIntegerField(default = 0)
    


    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)


    def __str__(self) -> str:
        return self.product_name
    

    def get_product_by_edition(self,edition):
        try:
            edition_variant = EditionVariant.objects.get(name=edition)
            return self.price + edition_variant.price
        except EditionVariant.DoesNotExist:
            return self.price
        
    def has_stock(self):

        return self.stock_quantity > 0
    


class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants', null=True, blank=True)
    variant = models.ForeignKey(EditionVariant, on_delete=models.CASCADE, related_name='product_variants', null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    def has_stock(self):
        return self.stock_quantity > 0 

    



class ProductImage(BaseModel):
    product = models.ForeignKey(Product,on_delete = models.CASCADE, related_name = 'product_images' )
    image = models.ImageField(upload_to="product")


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length = 10)
    is_expired = models.BooleanField(default = False)
    discount_price = models.IntegerField(default = 100)
    minimum_amount = models.IntegerField(default = 500)
    created_at = models.DateTimeField(auto_now_add=True )
    coupon_count = models.IntegerField(default=10)
    expiration_date = models.DateTimeField(default=timezone.now())
    carts_used = models.ManyToManyField('accounts.Cart', blank=True, related_name='used_coupons')

    def __str__(self) -> str:
        return self.coupon_code
    def save(self, *args, **kwargs):
        
        if isinstance(self.expiration_date, str):
            self.expiration_date = datetime.strptime(self.expiration_date, '%Y-%m-%dT%H:%M')
        if timezone.is_naive(self.expiration_date):
            self.expiration_date = timezone.make_aware(self.expiration_date, timezone.get_default_timezone())

        
        self.is_expired = timezone.now() > self.expiration_date or self.coupon_count == 0

        super().save(*args, **kwargs)
class Audiobook(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    audio_link = models.URLField()
    duration = models.DurationField()




class Ebook(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='ebook')
    ebook_file = models.FileField(upload_to='ebooks')
    

    def __str__(self):
        return f"Ebook for {self.product.product_name}"


