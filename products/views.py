from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render, redirect
from products.models import Product, Category, SubCategory, EditionVariant, LanguageVariant
from accounts.models import Cart, CartItem
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage

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

    



from django.db.models import Q

def all_products(request, category_slug = None):
    search_term = request.GET.get('search')
    
    if category_slug:
        categories  = Category.objects.exclude(slug = category_slug)
        category = get_object_or_404(Category, slug=category_slug)
        queryset = Product.objects.filter(category = category, is_listed = True,is_category_listed = True)
        if request.method == "POST":
            print('METHOD IS POST', request.POST)
            filter = request.POST.get('sortOption')
            if filter == 'lowToHigh':
                queryset = queryset.order_by('price')
            elif filter == 'highToLow':
                queryset = queryset.order_by('-price')
            elif filter =='relevance':
                return redirect('all_products_bycat',category_slug )
            context = {
            'categories': categories,
            'products': queryset,
            'category_option': category,
            'filter_option':filter,
            }

            

            return render(request, 'home/shop.html', context)


                  
    else:
         category = None
         categories  = Category.objects.all()
         queryset = Product.objects.filter(is_listed = True, is_category_listed = True)
         if request.method == "POST":
            print('METHOD IS POST', request.POST)
            filter = request.POST.get('sortOption')
            if filter == 'lowToHigh':
                queryset = queryset.order_by('price')
            elif filter == 'highToLow':
                queryset = queryset.order_by('-price')
            elif filter =='relevance':
                return redirect('all_products')
            context = {
            'categories': categories,
            'products': queryset,
            'category_option': category,
            'filter_option':filter,
            }

            

            return render(request, 'home/shop.html', context)

    if search_term:
        queryset = queryset.filter(Q(product_name__icontains = search_term))
    
    
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 8)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(page)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)



    context = {
        'categories': categories,
        'products': queryset,
        'category_option': category,
        
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


