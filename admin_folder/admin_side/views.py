
import json
import re
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import Profile
from products.models import Product, Category, SubCategory, ProductImage, LanguageVariant, EditionVariant
from .forms import LanguageVariantForm, EditionVariantForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, OrderItem

# Create your views here.
# ------------------------------------------------ACCOUNTS-------------------------------------------------------------
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

def admin_login(request):

    if  request.user.is_authenticated:
        if request.user.is_superuser:

            return redirect('admin_index')
        else:
            messages.warning(request, "You can't access the admin page")
            return render(request, 'admin_accounts/admin_login.html')

    if request.method == "POST":
        username = request.POST.get('username_admin')
        password = request.POST.get('password')

        if not (username and password):  # Check if email and password are not empty
            messages.warning(request, "Please enter email and password")
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, "Account Not Found")
            return HttpResponseRedirect(request.path_info)

        user = user_obj.first()
        

        user_obj = authenticate(username=username, password=password)
        if user_obj and user_obj.is_superuser:
            login(request, user_obj)
            return redirect("admin_index")
        elif user_obj:
            messages.warning(request, "You are not an admin")
            return redirect('admin_login')
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('admin_login')

    return render(request, 'admin_accounts/admin_login.html')
    
def admin_logout(request):

    
    logout(request)
    return redirect('admin_login')

# ----------------------------------------------------HOME------------------------------
@user_passes_test(is_superuser, login_url='admin_login')
def admin_index(request):
    return render(request, "admin_home/admin_index.html")

# -----------------------------------------------USERS-------------------------------
@user_passes_test(is_superuser, login_url='admin_login')
def admin_users(request):
    users_with_profiles = User.objects.filter(profile__isnull=False)
    context = {'profiles': users_with_profiles}
    return render(request, "admin_home/admin_user.html", context)

@user_passes_test(is_superuser, login_url='admin_login')
def admin_user_details(request, details_pk):
    profile = get_object_or_404(Profile, user_id=details_pk)
    user = profile.user
    print(f"User ID: {user.id}")

    orders = Order.objects.filter(user_id=user.id)
    print(f"Orders: {orders}")

    order_items = OrderItem.objects.filter(order__in=orders)
    print(f"Order Items: {order_items}")

    context = {'user':profile,
               'user_obj':user, 
               'orders': orders,
               'order_items': order_items,
               }
    return render(request, "admin_home/admin_user_details.html",context )

@user_passes_test(is_superuser, login_url='admin_login')
def block_unblock_user(request, block_pk):
    profile = get_object_or_404(Profile, user_id = block_pk)
    user = profile.user
    
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')
# ---------------------------------------CATEGORIES-----------------------------------
@user_passes_test(is_superuser, login_url='admin_login')
def admin_category(request):
    if request.method == "POST":
        new_category = request.POST.get('category_name')
        description = request.POST.get('description')
        try:
            if new_category and description is not None:
                if new_category.strip() and description.strip():
                    
                    existing_category = Category.objects.filter(category_name=new_category).first()
                    if existing_category:
                        messages.error(request, 'Category already exists.')
                        return redirect('admin_category')
                    cat = Category.objects.create(category_name = new_category, description = description )
                    cat.save()
                    messages.success(request, 'Category Successfully created')
                    return redirect('admin_category')
                else:
                    messages.error(request, 'Field(s) cannot be emptyspaces')
                    return redirect('admin_category')
            
            else:
                messages.error(request, 'Field(s) cannot be empty')
                return redirect('admin_category')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('admin_category')



    category = Category.objects.filter()
    context = {'categories': category}
    return render(request, 'admin_home/admin_category.html', context)


@user_passes_test(is_superuser, login_url='admin_login')
def unlist_category(request):
    try:
        # Decode JSON data from request body
        data = json.loads(request.body.decode('utf-8'))
        category_slug = data.get('category_slug', None)

        if category_slug is not None:
            category = Category.objects.get(slug=category_slug)
            print(category)
            category.is_listed = not category.is_listed
            category.save()

            Product.objects.filter(category = category).update(is_category_listed = category.is_listed)

            response_data = {
                'status': 'success',
                'message': 'Category status updated successfully',
                'is_listed': category.is_listed,
            }

            return JsonResponse(response_data)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data. Category slug not provided'})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Category not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@user_passes_test(is_superuser, login_url='admin_login')
def admin_category_detail(request, slug):
    category = Category.objects.get(slug = slug)
    sub_category = SubCategory.objects.filter(category = category)


    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')

        try:
            if category_name and description is not None:
                    
                    if category_name.strip() and description.strip():
                        


                    
                        category.category_name = category_name
                        category.description = description
                        category.save() 
                        messages.success(request, 'Category Edited successfully')

                        return redirect('admin_category_detail', slug=slug)
                    else:
                        messages.error(request, 'Field(s) cannot be emptyspaces')
                        return redirect('admin_category_detail', slug=slug)
            else:
                messages.error(request, 'Field(s) cannot be empty')
                return redirect('admin_category_detail', slug=slug)
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('admin_category_detail', slug=slug)


    context = {
            'category':category,
             'sub_categories': sub_category
    }
    return render(request, 'admin_home/admin_category_detail.html', context)

# views.py
# --------------------------------------------------SUBCATEGORY-----------------------------

@user_passes_test(is_superuser, login_url='admin_login')
def admin_subcategory(request, slug):
    
    category = Category.objects.get(slug = slug)
    subcategories = SubCategory.objects.filter(category=category)
    

    if request.method == 'POST':
        subcategory_name = request.POST.get('subcategory_name')
        subcategory_description = request.POST.get('subcategory_description')
        

        try:
            if subcategory_name is not None and subcategory_description is not None:


                if subcategory_name.strip() and subcategory_description.strip(): 
                        
                        
                        new_subcategory = SubCategory(
                            subcategory_name=subcategory_name,
                            description=subcategory_description,
                            category = category)
                        new_subcategory.save()
                        messages.success(request, 'Sub category added Successfully')
                        return redirect('admin_category_detail',slug=slug)
                else:
                    messages.error(request, 'Field(s) cannot be empty')
                    return redirect('admin_subcategory', slug=slug)


            else:
                messages.error(request, 'Field(s) cannot be empty')
                return redirect('admin_subcategory', slug=slug)
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('admin_subcategory', slug=slug)
    context = {
        'category': category,
        'subcategories': subcategories
    }


    return render(request, 'admin_home/admin_subcategory.html', context)

# -------------------------------------VARIANCES------------------------------------------------
def admin_variance(request):
    if request.method == 'POST':
        if 'language_name' in request.POST:
            language_name = request.POST.get('language_name')
            language_price = request.POST.get('language_price')

            if not re.match(r'^[a-zA-Z\s]+$', language_name):
                messages.error(request, 'Language name should not be empty and should contain only letters and spaces.')
                return redirect('admin_variance')
            
            if not language_name.strip():  
                messages.error(request, 'Language name should not be only empty spaces.')
                return redirect('admin_variance')
            
            if not language_price:
                messages.error(request, 'Price difference should not be empty.')
                return redirect('admin_variance')
            
            if LanguageVariant.objects.filter(name=language_name).exists():
                messages.error(request, f'Language variant with name {language_name} already exists.')
                return redirect('admin_variance')

            variant = LanguageVariant.objects.create(name = language_name, price = language_price)
            variant.save()
            messages.success(request, 'Created Successfully')
            
            return redirect('admin_variance')
            
        elif 'edition_name' in request.POST:
            edition_name = request.POST.get('edition_name')
            edition_price = request.POST.get('edition_price')

            if not re.match(r'^[a-zA-Z\s]+$', edition_name):
                messages.error(request, 'Edition name should not be empty and should contain only letters and spaces.')
                return redirect('admin_variance')

            if not edition_name.strip():  
                messages.error(request, 'Edition name should not be only empty spaces.')
                return redirect('admin_variance')

            if not edition_price:
                messages.error(request, 'Price difference should not be empty.')
                return redirect('admin_variance')

            
            if EditionVariant.objects.filter(name=edition_name).exists():
                messages.error(request, f'Edition variant with name {edition_name} already exists.')
                return redirect('admin_variance')

            variant = EditionVariant.objects.create(name = edition_name, price = edition_price)
            variant.save()
            messages.success(request, 'Created Successfully')
            
            return redirect('admin_variance')
            
    
    languages = LanguageVariant.objects.all()
    editions = EditionVariant.objects.all()
        
    
    context = {
        'languages':languages,
        'editions':editions,
    }
        
        
    return render(request, 'admin_home/admin_variance.html', context)

def admin_variance_detail(request, uid = None):
    if uid == None:
        context = {'nothing':True}
        return render(request, 'admin_home/admin_variance_detail.html', context)
    else:

        language_variant = LanguageVariant.objects.filter(uid = uid).first()
        edition_variant = EditionVariant.objects.filter(uid = uid).first()


        if language_variant:
            variant = LanguageVariant.objects.filter(uid = uid).first()
            context = {'variant':variant}


        elif edition_variant:
            variant = EditionVariant.objects.filter(uid = uid).first()
            context = {'variant':variant}

        return render(request, 'admin_home/admin_variance_detail.html', context)


def admin_edit_variant(request, uid):

    if request.method == "POST":
        variant_name = request.POST.get('variant_name')
        price = request.POST.get('price')
        print(request.POST)

        print(variant_name)
        print(price)
        
        language_variant = LanguageVariant.objects.filter(uid = uid).first()
        if language_variant:
            if not re.match(r'^[a-zA-Z\s]+$', variant_name):
                messages.error(request, 'Edition name should not be empty and should contain only letters and spaces.')
                return redirect('admin_language_variance_detail', language_uid = uid)

            
            if not variant_name.strip():  
                messages.error(request, 'Variant name should not be only empty spaces.')
                return redirect('admin_language_variance_detail', language_uid = uid)

            if not price:
                messages.error(request, 'Price difference should not be empty.')
                return redirect('admin_language_variance_detail', language_uid = uid)
        
            language_variant.name = variant_name
            language_variant.price = price

            language_variant.save()
            messages.success(request, 'Variant details  Updated Successfully')
            return redirect('admin_variance_detail', uid = uid)
        


        edition_variant = EditionVariant.objects.filter(uid = uid).first()
        print(edition_variant)
        if edition_variant:

            if not re.match(r'^[a-zA-Z\s]+$', variant_name):
                messages.error(request, 'Edition name should not be empty and should contain only letters and spaces.')
                return redirect('admin_variance_detail', edition_uid = uid)
            if not variant_name.strip():  
                messages.error(request, 'Variant name should not be only empty spaces.')
                return redirect('admin_variance_detail', edition_uid = uid)

            if not price:
                messages.error(request, 'Price difference should not be empty.')
                return redirect('admin_variance_detail', edition_uid = uid)

            edition_variant.name = variant_name
            edition_variant.price = price

            edition_variant.save()
            messages.success(request, 'Variant details  Updated Successfully')
            return redirect('admin_variance_detail', uid = uid)
    return redirect('admin_variance')




from django.shortcuts import get_object_or_404

def delete_variant(request, uid):
   
    language_variant = LanguageVariant.objects.filter(uid = uid).first()

    if language_variant:
        
        language_variant.delete()
        messages.warning(request, 'Language Variant Deleted Successfully')
        return redirect('admin_variance_detail')

   
    edition_variant = EditionVariant.objects.filter(uid = uid).first()

    if edition_variant:
        
        edition_variant.delete()
        messages.warning(request, 'Edition Variant Deleted Successfully')
        return redirect('admin_variance_detail')


    messages.error(request, 'Invalid Variant UID')
    return redirect('admin_variance')

@login_required
def admin_order(request):
    orders = Order.objects.all().order_by('-created_at')
    print(f"Number of orders: {orders.count()}")

    order_items_dict = {}  

    for order in orders:
       
        order_items = OrderItem.objects.filter(order=order)
        order_items_dict[order] = order_items
        
    order_status_choices = Order.ORDER_STATUS_CHOICES
        
    context = {
        'orders': orders,
        'order_items_dict': order_items_dict,
        'order_status_choices': order_status_choices,
    }

    return render(request, 'admin_home/admin_order.html', context)


@login_required
def admin_order_item(request, uid):
    order = Order.objects.get(uid=uid)
    order_items = OrderItem.objects.filter(order = order)
    item_status_choices = OrderItem.ORDER_STATUS_CHOICES
    print(item_status_choices)

    context = {'order': order,
             'order_items':order_items,
             'item_status_choices':item_status_choices,
             }  
    
    return render(request, 'admin_home/admin_order_item.html', context)


def admin_item_detail(request, uid):
    item = OrderItem.objects.get(uid = uid)
    item_status_choices = OrderItem.ORDER_STATUS_CHOICES
    context = {'item':item,
               'item_status_choices':item_status_choices,}
    return render(request, 'admin_home/admin_order_detail.html', context)



def update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_uid = data.get('order_uid')
            new_status = data.get('new_status')

            order = Order.objects.get(uid=order_uid)
            order.order_status = new_status
            order.save()

            if new_status == Order.DELIVERED:
                order.is_delivered = True
                order.save()

            return JsonResponse({'status': 'success', 'new_status': order.order_status})
        except Exception as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': 'Failed to update order status'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def update_order_item_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_uid = data.get('item_uid')
            new_status = data.get('new_status')
            print(item_uid)
            print(new_status)

            item = OrderItem.objects.get(uid=item_uid)
            item.order_status = new_status
            item.save()
            print(item.order_status)

            if new_status == Order.DELIVERED:
                item.is_delivered = True
                item.save()

            return JsonResponse({'status': 'success', 'new_status': item.order_status})
        except Exception as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': 'Failed to update order status'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_POST
def admin_cancel_order(request):
    try:
        data = json.loads(request.body)
        order_uid = data.get('order_uid')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})

    order = get_object_or_404(Order, uid=order_uid)

    if order.is_active:
        order.is_active = False
        order.save()
        response_data = {'success': True, 'message': 'Order is cancelled'}
    else:
        response_data = {'success': False, 'message': 'Order is already cancelled'}

    return JsonResponse(response_data)


@require_POST
def admin_cancel_item(request):
    
    try:
        data = json.loads(request.body)
        item_uid = data.get('item_uid')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})

    order_item = get_object_or_404(OrderItem, uid=item_uid)
    print('Ho')

    if order_item.is_active:
        order_item.is_active = False
        order_item.save()
        response_data = {'success': True, 'message': 'Order is cancelled'}
    else:
        response_data = {'success': False, 'message': 'Order is already cancelled'}

    return JsonResponse(response_data)







# def admin_product(request):
#     category = Category.objects.all()
#     products = Product.objects.all()

#     context = {
#         'categories':category,
#         "products": products 
#     }
#     return render(request, 'admin_home/admin_product.html', context)

# def products_by_category(request, slug):
#     category = Category.objects.get(slug = slug)
#     products = Product.objects.filter(category = category)
#     context = {
#          "products": products, 
#          'category_option':category
#          }
#     return render(request, 'admin_home/admin_product.html', context)
@user_passes_test(is_superuser, login_url='admin_login')
def admin_product(request, slug = None):
    
    products = Product.objects.all().order_by('product_name')

    if slug:
        categories  = Category.objects.exclude(slug = slug)
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category = category)
    else:
         category = None
         categories  = Category.objects.all()


    context = {
        'categories': categories,
        'products': products,
        'category_option': category
    }

    return render(request, 'admin_home/admin_product.html', context)


@user_passes_test(is_superuser, login_url='admin_login')
def admin_add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        price = request.POST.get('regular_price')
        promotional_price = request.POST.get('promotional_price')
        tax_rate = request.POST.get('tax_rate')
        currency = request.POST.get('currency')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('sub_category')
        print(product_name)
        print(category_id)
        print(subcategory_id)

        category = Category.objects.get(category_name=category_id)
        subcategory = SubCategory.objects.get(subcategory_name=subcategory_id)

        if Product.objects.filter(product_name = product_name).exists():
            messages.warning(request, 'A product with the same name already exists.')
            return redirect('admin_add_product')
        else:
                       
            new_product = Product.objects.create(
            product_name = product_name,
            product_description = product_description,
            price = price,
            regular_price = price,
            promotional_price = promotional_price,
            currency = currency,
            tax_rate = tax_rate,
            category = category,
            sub_category = subcategory
        
        )


        new_product.save()
        messages.success(request, 'Product added successfully!')
        upload_images = request.FILES.getlist('images')
        print(upload_images)
    
        for image in upload_images:
            image_upload(new_product, image)
            

        
        categories = Category.objects.all()
        subcategories = SubCategory.objects.all()

        
        product = Product.objects.get(slug = new_product.slug )
        context = {'product': product, 
                   'categories':categories,
                   'subcategories':subcategories,
                   }
        
        return render(request, 'admin_home/admin_add_product.html', context)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    context = {
        'categories':categories,
        'subcategories':subcategories,
    }
        

    return render(request, 'admin_home/admin_add_product.html', context)


def image_upload(product, image):
    print(product)
    new_product_image = ProductImage(product = product, image = image)
    new_product_image.save()






@user_passes_test(is_superuser, login_url='admin_login')
def admin_edit_product(request, product_slug):
    product = Product.objects.get(slug=product_slug)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    product_images = ProductImage.objects.filter(product=product)

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.product_description = request.POST.get('product_description')
        product.price = request.POST.get('regular_price')
        product.promotional_price = request.POST.get('promotional_price')
        product.tax_rate = request.POST.get('tax_rate')
        product.currency = request.POST.get('currency')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('sub_category')
        print(category_id)
        print(subcategory_id)

        category = Category.objects.get(slug=category_id)
        subcategory = SubCategory.objects.get(sub_slug=subcategory_id)

        product.category = category
        product.sub_category = subcategory
        product.save()
        request.session['success_message'] = 'Product edited successfully'
        return redirect('admin_product')

    context = {
        'product': product,
        'categories':categories,
        'subcategories':subcategories,
        'product_images': product_images,
        }
    

    return render(request,'admin_home/edit_product.html', context)

from django.http import JsonResponse

from django.http import JsonResponse

def admin_change_image(request):
    if request.method == 'POST':
        image_uid = request.POST.get('image_uid')
        new_image_file = request.FILES.get('new_image')

        try:
            image_object = ProductImage.objects.get(uid=image_uid)
            image_object.image = new_image_file
            image_object.save()

            # Retrieve all images for the associated product
            product_images = ProductImage.objects.filter(product=image_object.product)

            # Create a list of dictionaries containing image data
            updated_images = [{'image': image.image.url, 'uid': image.uid} for image in product_images]

            return JsonResponse({'success': True, 'message': 'Image changed successfully', 'images': updated_images})
        except ProductImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Image not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    # Return a default response if the request method is not POST
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_sub_categories(request):
    if request.method=='POST':
        cat=json.load(request)['category']
        if cat=='':
            data={'sub_categories':''}
        else:
            c=Category.objects.get(category_name=cat)
            sub_categories=c.category.all()
            print(sub_categories)
            sub_categories_list = list(sub_categories.values())
            data={'sub_categories':sub_categories_list}
    else:
        data={'sub_categories':'Invalid HTTP method'}
        return JsonResponse(data)
    return JsonResponse(data)


@user_passes_test(is_superuser, login_url='admin_login')
def unlist_product(request, product_slug):
    product = Product.objects.get(slug = product_slug)
    product.is_listed = not product.is_listed
    product.save()

    return redirect(admin_product)


