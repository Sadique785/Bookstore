from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render, redirect
from products.models import Product, Category, SubCategory, EditionVariant, LanguageVariant
from accounts.models import Cart, CartItem

# Create your views here.

def get_product(request, product_slug):


    
    try:
        product = Product.objects.get(slug = product_slug)
        context = {'product':product }

        if request.GET.get('edition'):
            edition = request.GET.get('edition')
            price = product.get_product_by_edition(edition)

            context['selected_edition'] = edition
            context['updated_price'] = price

            print(price)

        # if request.GET.get('language'):
        #     language = request.GET.get('language')
        #     new_price = product.get_product_by_language(language)

        #     context['selected_language'] = language
        #     context['new_price'] = new_price

        #     print(new_price)

        return render(request, 'home/product.html', context = context)
    
        
    
    except Exception as e:
        print(e)
        return HttpResponse("An error occurred. Please try again later.")

    





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


def add_to_cart(request, uid):
    variant = request.GET.get('variant')

    
        

    product = Product.objects.get(uid = uid)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)

    cart_item = CartItem.objects.create(cart = cart, product = product, )

    if variant:
        variant = request.GET.get('variant')
        edititon_variant = EditionVariant.objects.get(name = variant)
        cart_item.edition_variant = edititon_variant
        cart_item.save()


    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


