from django.http import Http404
from django.shortcuts import get_object_or_404, render
from products.models import Product, Category, SubCategory

# Create your views here.

def get_product(request, product_slug):
    try:
        product = Product.objects.get(slug = product_slug)
        return render(request, 'home/product.html', context = {'product':product })
    
    
    except Product.DoesNotExist:
        raise Http404("Product does not exist")

def all_products(request, category_slug = None):
    if category_slug:
        categories  = Category.objects.exclude(slug = category_slug)
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = category, is_listed = True,is_category_listed = True)
    else:
         category = None
         categories  = Category.objects.all()
         products = Product.objects.filter(is_listed = True, is_category_listed = True)

    context = {
        'categories': categories,
        'products': products,
        'category_option': category
    }

    
    
    return render(request, 'home/shop.html', context)