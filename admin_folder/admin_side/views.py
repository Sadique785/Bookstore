
import json
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import Profile
from products.models import Product, Category, SubCategory, ProductImage
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

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


@user_passes_test(is_superuser, login_url='admin_login')
def admin_index(request):
    return render(request, "admin_home/admin_index.html")


@user_passes_test(is_superuser, login_url='admin_login')
def admin_users(request):
    users_with_profiles = User.objects.filter(profile__isnull=False)
    context = {'profiles': users_with_profiles}
    return render(request, "admin_home/admin_user.html", context)

@user_passes_test(is_superuser, login_url='admin_login')
def admin_user_details(request, details_pk):
    user = Profile.objects.get(user_id = details_pk )
    # user1 = Profile.objects.get(id = pk)
    context = {'user':user}
    # context2 = {'user1':user1}
    return render(request, "admin_home/admin_user_details.html",context )

@user_passes_test(is_superuser, login_url='admin_login')
def block_unblock_user(request, block_pk):
    profile = get_object_or_404(Profile, user_id = block_pk)
    user = profile.user
    
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')

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


