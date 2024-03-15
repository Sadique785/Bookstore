
from io import BytesIO
import json
import re
from django.db.models import F
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from accounts.models import Profile, Transaction, Wallet
from products.models import Product, Category, SubCategory, ProductImage, LanguageVariant, EditionVariant, Coupon, ProductVariant
from .forms import LanguageVariantForm, EditionVariantForm
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, OrderItem
from django.views.decorators.cache import cache_control
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.utils import timezone
import pytz
from django.db.models import Sum
from django.db.models import Q
from home.models import Banner
from django.db import transaction
import pandas as pd
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist



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

        if not (username and password):  
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







def best_selling_products():
    best_selling_product_name = OrderItem.objects.filter(is_paid = True).values('product_name','price').annotate(total_quantity = Sum('quantity')).order_by('-total_quantity')[:5]   
    best_selling_product_names = [entry['product_name'] for entry in best_selling_product_name]
    best_selling_quantities = [entry['total_quantity'] for entry in best_selling_product_name]
    best_selling_prices = [entry['price'] for entry in best_selling_product_name]
    list_of_items = []

    for name, quantity, price in zip(best_selling_product_names, best_selling_quantities, best_selling_prices):
        product = Product.objects.filter(product_name = name).first()
        
        if name :
            revenue = price * quantity
            list_of_items.append([product, quantity, revenue])

    return list_of_items



def best_selling_categories():
    best_selling_product_names = OrderItem.objects.filter(is_paid=True).values('product_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    best_selling_product_names = [entry['product_name'] for entry in best_selling_product_names]

    best_selling_categories = {}
    for product_name in best_selling_product_names:
        product = Product.objects.filter(product_name=product_name).first()

        


        if product:
            category = product.category
            total_quantity = OrderItem.objects.filter(is_paid=True, product_name=product_name).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            total_revenue = OrderItem.objects.filter(is_paid=True, product_name=product_name).aggregate(total_revenue=Sum(F('quantity') * F('price')))['total_revenue']

            if category in best_selling_categories:

                best_selling_categories[category]['total_quantity'] += total_quantity
                best_selling_categories[category]['total_revenue'] += total_revenue


            else:
                best_selling_categories[category] = {
                    'total_quantity': total_quantity,
                    'total_revenue': total_revenue,
                }

    return best_selling_categories



# ----------------------------------------------------HOME------------------------------
@user_passes_test(is_superuser, login_url='admin_login')
def admin_index(request):


    total_revenue = Order.objects.filter(is_delivered=True).aggregate(Sum('total_amount'))['total_amount__sum']
    total_count = Order.objects.filter(is_delivered = True).count()
    product_count = Product.objects.all().count()
    category_count = Category.objects.all().count()
    best_products = best_selling_products()
    best_categories = best_selling_categories()


    if total_count > 0:
        monthly_revenue = total_revenue // total_count
    else:
        monthly_revenue = 0



    if total_revenue is None:
        total_revenue = 0
    if total_count is None:
        total_count = 0
    if product_count is None:
        product_count = 0
    if category_count is None:
        category_count = 0



    custom_year = 2024


    today = timezone.now()
    last_12_months = [today - relativedelta(months=i) for i in range(11, -1, -1)]

    last_12_months_custom_year = [
        timezone.datetime(custom_year, month.month, 1, tzinfo=pytz.UTC) 
        for month in last_12_months
    ]

    month_labels = [month.strftime('%b') for month in last_12_months_custom_year]

    products_count_data = []
    order_items_count_data = []
    user_count_data = []

    for start_date in last_12_months_custom_year:
        end_date = start_date + relativedelta(day=31, hour=23, minute=59, second=59)

        products_count_for_month = Product.objects.filter(created_at__range=(start_date, end_date)).count()
        products_count_data.append(products_count_for_month)

        order_items_count_for_month = OrderItem.objects.filter(created_at__range=(start_date, end_date), is_delivered=True).count()
        order_items_count_data.append(order_items_count_for_month)

        user_count_for_month = Profile.objects.filter(created_at__range=(start_date, end_date)).count()
        user_count_data.append(user_count_for_month)


    monthly_data ={'product_count': products_count_data,
        'order_count': order_items_count_data,
        'user_count': user_count_data,

    }



# -------------------------------Weeekly data-----------------------
    selected_month = 2

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_12_weeks = [today - relativedelta(weeks=i) for i in range(11, -1, -1)]

    week_labels = [week.strftime('%d %b') for week in last_12_weeks]
    selected_month_start = timezone.datetime(custom_year, selected_month, 1, tzinfo=pytz.UTC)
    selected_month_end = (selected_month_start + relativedelta(months=1) - relativedelta(seconds=1))

    weekly_products_count_data = []
    weekly_order_items_count_data = []
    weekly_user_count_data = []

    for start_date in last_12_weeks:
        end_date = start_date + relativedelta(days=6, hour=23, minute=59, second=59)


        if selected_month_start <= start_date <= selected_month_end or selected_month_start <= end_date <= selected_month_end:

            weekly_products_count = Product.objects.filter(created_at__range=(start_date, end_date)).count()
            weekly_products_count_data.append(weekly_products_count)

            weekly_order_items_count = OrderItem.objects.filter(created_at__range=(start_date, end_date), is_delivered=True).count()
            weekly_order_items_count_data.append(weekly_order_items_count)

            weekly_user_count = Profile.objects.filter(created_at__range=(start_date, end_date)).count()
            weekly_user_count_data.append(weekly_user_count)

    weekly_data = {
        'product_count': weekly_products_count_data,
        'order_count': weekly_order_items_count_data,
        'user_count': weekly_user_count_data,
    }


# ---------------------------------------daily_data------------------------

    selected_week = 3
    selected_week_start = selected_month_start + relativedelta(weeks=selected_week - 1)
    selected_week_end = selected_week_start + relativedelta(weeks=1, days=-1, hour=23, minute=59, second=59)
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # last_12_days = [today - relativedelta(days=i) for i in range(11, -1, -1)]
    last_7_days = [selected_week_start + relativedelta(days=i) for i in range(6, -1, -1)]

    day_labels = [day.strftime('%d %b') for day in last_7_days]

    daily_products_count_data = []
    daily_order_items_count_data = []
    daily_user_count_data = []

    for start_date in last_7_days:
        end_date = start_date + relativedelta(hour=23, minute=59, second=59)

        daily_products_count = Product.objects.filter(created_at__range=(start_date, end_date)).count()
        daily_products_count_data.append(daily_products_count)

        daily_order_items_count = OrderItem.objects.filter(created_at__range=(start_date, end_date), is_delivered=True).count()
        daily_order_items_count_data.append(daily_order_items_count)

        daily_user_count = Profile.objects.filter(created_at__range=(start_date, end_date)).count()
        daily_user_count_data.append(daily_user_count)

    daily_data = {
        'product_count': daily_products_count_data,
        'order_count': daily_order_items_count_data,
        'user_count': daily_user_count_data,
    }

    new_profiles = Profile.objects.all().order_by('-created_at')[:3]






    context = {
        
        'month_labels': month_labels,
        'monthly_data':monthly_data,
        'weekly_data':weekly_data,
        'week_labels': week_labels,
        'day_labels': day_labels,
        'daily_data': daily_data,
        'total_revenue':total_revenue,
        'monthly_revenue':monthly_revenue,
        'category_count':category_count,
        'product_count':product_count,
        'total_revenue':total_revenue,
        'total_count':total_count,
        'best_products':best_products,
        'best_categories':best_categories,
        'new_profiles':new_profiles,
        
    }

    return render(request, "admin_home/admin_index.html", context)





def calculate_selected_week(selected_day):
    week_ranges = [
        (1, 8), (9, 15), (16, 22), (23, 31)
    ]

    for week, (start_day, end_day) in enumerate(week_ranges, start=1):
        if start_day <= selected_day <= end_day:
            return week

    return None



def filter_chart(request):


    if request.method == 'POST':
        
        data = json.loads(request.body.decode('utf-8'))
        selected_date = data.get('date')

        

        selected_datetime = datetime.strptime(selected_date, "%Y-%m-%d")
        print(selected_datetime)

        custom_year = selected_datetime.year
        selected_month = selected_datetime.month
        selected_day = selected_datetime.day
        selected_week = calculate_selected_week(selected_day)

        print(custom_year)
        print(selected_month)
        print(selected_day)
        print(selected_week)




        

        
    # ------------------Monthly data-------------------------
        today = timezone.now()
        last_12_months = [today - relativedelta(months=i) for i in range(11, -1, -1)]

        last_12_months_custom_year = [
            timezone.datetime(custom_year, month.month, 1, tzinfo=pytz.UTC) 
            for month in last_12_months
        ]

        month_labels = [month.strftime('%b') for month in last_12_months_custom_year]

        products_count_data = []
        order_items_count_data = []
        user_count_data = []

        for start_date in last_12_months_custom_year:
            end_date = start_date + relativedelta(day=31, hour=23, minute=59, second=59)

            products_count_for_month = Product.objects.filter(created_at__range=(start_date, end_date)).count()
            products_count_data.append(products_count_for_month)

            order_items_count_for_month = OrderItem.objects.filter(created_at__range=(start_date, end_date), is_delivered=True).count()
            order_items_count_data.append(order_items_count_for_month)

            user_count_for_month = Profile.objects.filter(created_at__range=(start_date, end_date)).count()
            user_count_data.append(user_count_for_month)


        monthly_data ={'product_count': products_count_data,
            'order_count': order_items_count_data,
            'user_count': user_count_data,

        }



    # -------------------------------Weeekly data-----------------------
        

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        last_12_weeks = [today - relativedelta(weeks=i) for i in range(11, -1, -1)]

        week_labels = [week.strftime('%d %b') for week in last_12_weeks]
        selected_month_start = timezone.datetime(custom_year, selected_month, 1, tzinfo=pytz.UTC)
        selected_month_end = (selected_month_start + relativedelta(months=1) - relativedelta(seconds=1))

        weekly_products_count_data = []
        weekly_order_items_count_data = []
        weekly_user_count_data = []

        for start_date in last_12_weeks:
            end_date = start_date + relativedelta(days=6, hour=23, minute=59, second=59)


            if selected_month_start <= start_date <= selected_month_end or selected_month_start <= end_date <= selected_month_end:

                weekly_products_count = Product.objects.filter(created_at__range=(start_date, end_date)).count()
                weekly_products_count_data.append(weekly_products_count)

                weekly_order_items_count = OrderItem.objects.filter(created_at__range=(start_date, end_date), is_delivered=True).count()
                weekly_order_items_count_data.append(weekly_order_items_count)

                weekly_user_count = Profile.objects.filter(created_at__range=(start_date, end_date)).count()
                weekly_user_count_data.append(weekly_user_count)

        weekly_data = {
            'product_count': weekly_products_count_data,
            'order_count': weekly_order_items_count_data,
            'user_count': weekly_user_count_data,
        }


    # ---------------------------------------daily_data------------------------

        selected_week = 3
        selected_week_start = selected_month_start + relativedelta(weeks=selected_week - 1)
        selected_week_end = selected_week_start + relativedelta(weeks=1, days=-1, hour=23, minute=59, second=59)
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # last_12_days = [today - relativedelta(days=i) for i in range(11, -1, -1)]
        last_7_days = [selected_week_start + relativedelta(days=i) for i in range(6, -1, -1)]

        day_labels = [day.strftime('%d %b') for day in last_7_days]

        daily_products_count_data = []
        daily_order_items_count_data = []
        daily_user_count_data = []

        for start_date in last_7_days:
            end_date = start_date + relativedelta(hour=23, minute=59, second=59)

            daily_products_count = Product.objects.filter(created_at__range=(start_date, end_date)).count()
            daily_products_count_data.append(daily_products_count)

            daily_order_items_count = OrderItem.objects.filter(created_at__range=(start_date, end_date), is_delivered=True).count()
            daily_order_items_count_data.append(daily_order_items_count)

            daily_user_count = Profile.objects.filter(created_at__range=(start_date, end_date)).count()
            daily_user_count_data.append(daily_user_count)

        daily_data = {
            'product_count': daily_products_count_data,
            'order_count': daily_order_items_count_data,
            'user_count': daily_user_count_data,
        }

        
        return JsonResponse({
                'month_labels': month_labels,
                'monthly_data':monthly_data,
                'weekly_data':weekly_data,
                'week_labels': week_labels,
                'day_labels': day_labels,
                'daily_data': daily_data,
            })
    








# -----------------------------------------------USERS-------------------------------
    


@user_passes_test(is_superuser, login_url='admin_login')
def admin_users(request):
    query_set = Profile.objects.filter(user__isnull=False, is_email_verified = True)
    search_term = request.GET.get('search')
    query_set = query_set.order_by('-created_at')
    

    if search_term and search_term.lower() != 'none':
        query_set = query_set.filter(
            Q(user__first_name__icontains=search_term) | Q(user__last_name__icontains=search_term) | Q(user__email__icontains=search_term)
        )

    status_filter = request.GET.get('status')

    if status_filter == 'active':
        query_set = query_set.filter(user__is_active=True)
    elif status_filter == 'blocked':
        query_set = query_set.filter(user__is_active=False)
    else:
      
        status_filter = 'all'


    page = request.GET.get('page', 1)
    paginator = Paginator(query_set, 6)
    try:
        query_set = paginator.page(page)
    except PageNotAnInteger:
        query_set = paginator.page(page)
    except EmptyPage:
        query_set = paginator.page(paginator.num_pages)



    context = {'profiles': query_set, 'search_term': search_term, 'status_filter': status_filter}
    return render(request, "admin_home/admin_user.html", context)





@user_passes_test(is_superuser, login_url='admin_login')
def admin_user_details(request, details_pk):
    profile = get_object_or_404(Profile, user_id=details_pk)
    user = profile.user

    orders = Order.objects.filter(user_id=user.id)

    order_items = OrderItem.objects.filter(order__in=orders)

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


    for session in Session.objects.iterator():
            data = session.get_decoded()
            if '_auth_user_id' in data and str(data['_auth_user_id']) == str(user.id):

                session.delete()

    sessions = Session.objects.iterator() 
    for session in sessions: 
        data = session.get_decoded() 
        data["session_key"] = session.session_key

    user.is_active = not user.is_active
    user.save()

    
    return redirect('admin_users')
# ---------------------------------------CATEGORIES-----------------------------------




@user_passes_test(is_superuser, login_url='admin_login')
def admin_category(request):
    if request.method == "POST":
        new_category = request.POST.get('category')
        description = request.POST.get('description')

        try:
            if new_category is not None and description is not None:
                cleaned_category_name = re.sub(r'[^A-Za-z]', '', new_category).strip()
                if cleaned_category_name and description.strip():
                    existing_category = Category.objects.filter(category_name=cleaned_category_name).first()
                    if existing_category:
                        messages.error(request, 'Category already exists.')
                        return redirect('admin_category')

                    cat = Category.objects.create(category_name=cleaned_category_name, description=description)
                    cat.save()
                    messages.success(request, 'Category Successfully created')
                    return redirect('admin_category')
                else:
                    messages.error(request, 'Category name and description cannot be empty')
                    return redirect('admin_category')
            else:
                messages.error(request, 'Category name and description cannot be None')
                return redirect('admin_category')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('admin_category')



    query_set = Category.objects.filter()


    search_term = request.GET.get('search')

    if search_term:
        cleaned_search_term = re.sub(r'[^A-Za-z]', '', search_term)
        query_set = query_set.filter(Q(category_name__icontains=cleaned_search_term)).order_by('category_name')
        if not query_set:
            messages.warning(request, 'Nothing matches the query')
            return redirect('admin_category')

    context = {'categories': query_set, 'search_term':search_term}
    return render(request, 'admin_home/admin_category.html', context)




@user_passes_test(is_superuser, login_url='admin_login')
def unlist_category(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        category_slug = data.get('category_slug', None)

        if category_slug is not None:
            category = Category.objects.get(slug=category_slug)
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
    query_set = SubCategory.objects.filter(category = category)

    search_term = request.GET.get('search')

    if search_term:
        
        query_set = query_set.filter(Q(subcategory_name__icontains= search_term)).order_by('subcategory_name')
        if not query_set:
            messages.warning(request, 'Nothing matches the query')
            return redirect('admin_category')


    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')

        
        if category_name and description is not None:
                
                if category_name.strip() and description.strip():
                    existing_category = Category.objects.exclude(slug=slug).filter(category_name=category_name).first()
                    if existing_category:
                        messages.error(request, 'Category name already exists.')
                        return redirect('admin_category_detail', slug=slug)
                    
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
                
        


    context = {
            'category':category,
             'sub_categories': query_set,
             'search_term':search_term,
    }
    return render(request, 'admin_home/admin_category_detail.html', context)

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



@user_passes_test(is_superuser, login_url='admin_login')
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

@user_passes_test(is_superuser, login_url='admin_login')
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

@user_passes_test(is_superuser, login_url='admin_login')
def admin_edit_variant(request, uid):

    if request.method == "POST":
        variant_name = request.POST.get('variant_name')
        price = request.POST.get('price')

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
@user_passes_test(is_superuser, login_url='admin_login')
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
@user_passes_test(is_superuser, login_url='admin_login')
def admin_order(request):
    orders = Order.objects.all().order_by('-created_at')

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
@user_passes_test(is_superuser, login_url='admin_login')
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

@user_passes_test(is_superuser, login_url='admin_login')
def admin_item_detail(request, uid):
    item = OrderItem.objects.get(uid = uid)
    item_status_choices = OrderItem.ORDER_STATUS_CHOICES
    context = {'item':item,
               'item_status_choices':item_status_choices,}
    return render(request, 'admin_home/admin_order_detail.html', context)


@user_passes_test(is_superuser, login_url='admin_login')
def update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_uid = data.get('order_uid')
            new_status = data.get('new_status')

            order = Order.objects.get(uid=order_uid)
            order.order_status = new_status
            order.save()

            order_items = OrderItem.objects.filter(order = order)
            for item in order_items:
                item.order_status = new_status
                item.save()

            if new_status == Order.DELIVERED:
                order.is_delivered = True
                order.save()

                for item in order_items:
                    item.is_delivered = True
                    item.save()


            

            return JsonResponse({'status': 'success', 'new_status': order.order_status})
        except Exception as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': 'Failed to update order status'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@user_passes_test(is_superuser, login_url='admin_login')
def update_order_item_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_uid = data.get('item_uid')
            new_status = data.get('new_status')

            item = OrderItem.objects.get(uid=item_uid)
            item.order_status = new_status
            item.save()
            print(item.order_status)

            if new_status == Order.DELIVERED:
                item.is_delivered = True
                item.save()


            all_items_delivered = not item.order.order_items.filter(is_delivered=False).exists()

            if all_items_delivered:
                item.order.is_delivered = True
                item.order.save()

            print(item.order.is_delivered)



            



                

            return JsonResponse({'status': 'success', 'new_status': item.order_status})
        except Exception as e:
            print(str(e))
            return JsonResponse({'status': 'error', 'message': 'Failed to update order status'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@user_passes_test(is_superuser, login_url='admin_login')
@require_POST
def admin_cancel_order(request):
    try:
        data = json.loads(request.body)
        order_uid = data.get('order_uid')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})

    order = get_object_or_404(Order, uid=order_uid)
    user = order.user
    wallet = Wallet.objects.filter(user = user).first()
    if order.is_active:
        order.is_active = False
        order.save()


        
        order_items = order.order_items.all()
        total_price = 0
        for item in order_items:
            item.is_active = False
            if item.order_status is not None:
                item.order_status = None  
            
            price = item.get_total()
            total_price += price

            Wallet.objects.filter(uid=wallet.uid).update(balance=F('balance') + price)
            Wallet.objects.filter(uid=wallet.uid).update(refund=F('refund') + price)

            item.save()


        transaction = Transaction.objects.create(
                        wallet=wallet,
                        amount=total_price,
                        transaction_type='credit',
                        description='Added money to wallet',
                        )
        transaction.save()




        response_data = {'success': True, 'message': 'Order is cancelled'}
    else:
        response_data = {'success': False, 'message': 'Order is already cancelled'}

    return JsonResponse(response_data)


@user_passes_test(is_superuser, login_url='admin_login')
@require_POST
def admin_cancel_item(request):
    
    try:
        data = json.loads(request.body)
        item_uid = data.get('item_uid')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})

    order_item = get_object_or_404(OrderItem, uid=item_uid)
    order = order_item.order
    user = order.user
    wallet = Wallet.objects.filter(user = user).first()

    if order_item.is_active:
        order_item.is_active = False
        order_item.order_status = None  
        order_item.save()
        price = order_item.get_total()
            
        Wallet.objects.filter(uid=wallet.uid).update(balance=F('balance') + price)
        Wallet.objects.filter(uid=wallet.uid).update(refund=F('refund') + price)



        order_item.order.total_amount -= order_item.get_total()
        order_item.order.save()




        all_orders = order_item.order.order_items.all()

        
        all_items_cancelled = all(not order.is_active for order in all_orders)

        
        if all_items_cancelled:
            order_item.order.is_active = False
            order_item.order.save()
        

        transaction = Transaction.objects.create(
                        wallet=wallet,
                        amount=price,
                        transaction_type='credit',
                        description='Added money to wallet',
                        )
        transaction.save()




        response_data = {'success': True, 'message': 'Order is cancelled'}
    else:
        response_data = {'success': False, 'message': 'Order is already cancelled'}

    return JsonResponse(response_data)









@user_passes_test(is_superuser, login_url='admin_login')
def admin_product(request, slug=None):
    search_term = request.GET.get('search')
    category_options = request.GET.getlist('categories')  # Use getlist to get multiple selected categories
    categories = Category.objects.all()


    query_set = Product.objects.all().order_by('product_name')

    if category_options and 'all' not in category_options:
       
        query_set = query_set.filter(category__category_name__in=category_options)

    if search_term:
       
        query_set = query_set.filter(Q(product_name__icontains=search_term) | Q(category__category_name__icontains=search_term))

    page = request.GET.get('page', 1)
    paginator = Paginator(query_set, 8)
    try:
        query_set = paginator.page(page)
    except PageNotAnInteger:
        query_set = paginator.page(page)
    except EmptyPage:
        query_set = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'products': query_set , # Order the final result
        'search_term': search_term,
        'category_options': category_options,
    }

    return render(request, 'admin_home/admin_product.html', context)



@user_passes_test(is_superuser, login_url='admin_login')
def admin_stock(request):
    query_set = Product.objects.all().order_by('product_name')
    page = request.GET.get('page', 1)
    paginator = Paginator(query_set, 8)
    try:
        query_set = paginator.page(page)
    except PageNotAnInteger:
        query_set = paginator.page(page)
    except EmptyPage:
        query_set = paginator.page(paginator.num_pages)


    context = {
        'products':query_set,
    }
    return render(request, 'admin_home/admin_stock.html', context)

def admin_add_stock(request, slug):
    product = Product.objects.filter(slug = slug).first()

    try:
        variants = product.edition_variant.all()
    except ObjectDoesNotExist:
        variants = None


    if request.method == "POST":

        normal_stock = request.POST.get('normal_stock')

        if normal_stock is None or normal_stock == '':
            messages.warning(request, 'Please enter the stock quantity for the main product.')
            return redirect('admin_add_stock', slug=slug)
        

        product.stock_quantity = normal_stock
        product.save()

        if variants:
            for variant in variants:
                variant_stock = request.POST.get(f"{variant.name}_stock")


                if variant_stock is None or variant_stock == '':
                    messages.warning(request, f'Please enter the stock quantity for {variant.name}.')
                    return redirect('admin_add_stock', slug=slug)
                

                try:
                    existing_stock = ProductVariant.objects.get(product=product, variant=variant)
                    existing_stock.stock_quantity = variant_stock
                    existing_stock.save()
                except ProductVariant.DoesNotExist:
                    
                    ProductVariant.objects.create(product=product, variant=variant, stock_quantity=variant_stock)
        messages.success(request, 'Stock Successfully Updated')
        return redirect('admin_add_stock',slug)

    context = {
        'product':product,
        'variants':variants,
    }
    
    return render(request,'admin_home/admin_add_stock.html',context)



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
        edition_variant_names = request.POST.getlist('edition_variant')
        # stock_quantity = request.POST.get('stock')

        selected_editions = EditionVariant.objects.filter(name__in = edition_variant_names)


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
            sub_category = subcategory,
            # stock_quantity = stock_quantity,
            
        
        )
            
        if not selected_editions:
            new_product.save()
        else:
            new_product.edition_variant.add(*selected_editions)
            new_product.save()
            for variant in selected_editions:
                product_variant = ProductVariant.objects.create(product = new_product, variant = variant)
                product_variant.save()

        
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
    editions = EditionVariant.objects.all()
    context = {
        'categories':categories,
        'subcategories':subcategories,
        'editions':editions,
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
    editions = EditionVariant.objects.all()


    if request.method == 'POST':

        product.product_name = request.POST.get('product_name')
        product.product_description = request.POST.get('product_description')
        product.price = request.POST.get('regular_price')
        product.promotional_price = request.POST.get('promotional_price')
        product.tax_rate = request.POST.get('tax_rate')
        product.currency = request.POST.get('currency')
        category_id = request.POST.get('category') 
        subcategory_id = request.POST.get('sub_category')
        # product.stock_quantity = request.POST.get('stock')


        selected_editions = request.POST.getlist('edition_variant')


        if selected_editions:
            product.edition_variant.clear()
            for edition_name in selected_editions:
                edition = EditionVariant.objects.get(name = edition_name)
                product.edition_variant.add(edition)
        
        

        category = Category.objects.get(slug=category_id)
        subcategory = SubCategory.objects.get(sub_slug=subcategory_id)
        product.category = category
        product.sub_category = subcategory
        product.save()



        with transaction.atomic():
            product.save()

            # Update product images
            updated_images = request.FILES.getlist('images')
            for image in updated_images:
                image_upload(product, image)

        messages.success(request, 'Product edited successfully!')
        return redirect('admin_edit_product', product_slug=product_slug)
    

    context = {
        'product': product,
        'categories':categories,
        'subcategories':subcategories,
        'product_images': product_images,
        'editions':editions,
        }
    

    return render(request,'admin_home/edit_product.html', context)






from django.http import JsonResponse
@user_passes_test(is_superuser, login_url='admin_login')

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

import os
def admin_delete_image(request):
    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))

        image_uid = data['imageUid']
        image_object = ProductImage.objects.filter(uid = image_uid).first()

        image_path = os.path.join('your_image_directory', image_uid)
        image_object.delete()


        
        return JsonResponse({'success': True, 'message': 'Image Deleted successfully'})

    return JsonResponse({'success': True, 'message': 'Image Deleted successfully'})




def get_sub_categories(request):
    if request.method=='POST':
        cat=json.load(request)['category']
        if cat=='':
            data={'sub_categories':''}
        else:
            c=Category.objects.get(category_name=cat)
            sub_categories=c.category.all()
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

# -----------------------------------------------coupon section------------------------

@user_passes_test(is_superuser, login_url='admin_login')

def admin_coupon(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    context = {'coupons': coupons}

    return render(request, 'admin_home/admin_coupon.html', context)



@user_passes_test(is_superuser, login_url='admin_login')

def admin_add_coupon(request):
    if request.method == 'POST':
        # Extract form data
        coupon_code = request.POST.get('coupon_code', '').strip()
        discount_price = request.POST.get('discount_price')
        minimum_amount = request.POST.get('minimum_amount')
        coupon_count = request.POST.get('coupon_count')
        expiration_date = request.POST.get('expiration_date')
        expire_checkbox = request.POST.get('expireCheckbox')


        if not coupon_code:
            messages.error(request, 'Coupon code must not be empty or contain only spaces.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            messages.error(request, 'Coupon with the same code already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        coupon = Coupon(
            coupon_code=coupon_code,
            discount_price=discount_price,
            minimum_amount=minimum_amount,
            coupon_count=coupon_count,
            expiration_date=expiration_date,
            is_expired=bool(expire_checkbox), 
        )
        coupon.save()


        messages.success(request, 'Coupon added successfully!')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
    return render(request, 'admin_home/admin_add_coupon.html')


@user_passes_test(is_superuser, login_url='admin_login')

def admin_edit_coupon(request, coupon_uid):
    coupon = Coupon.objects.filter(uid = coupon_uid).first()
    context = {'coupon':coupon}

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        discount_price = request.POST.get('discount_price')
        minimum_amount = request.POST.get('minimum_amount')
        coupon_count = request.POST.get('coupon_count')
        expiration_date = request.POST.get('expiration_date')
        expire_checkbox = request.POST.get('expireCheckbox')

        if not coupon_code:
            messages.error(request, 'Coupon code must not be empty or contain only spaces.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        
        coupon.coupon_code=coupon_code
        coupon.discount_price=discount_price
        coupon.minimum_amount=minimum_amount
        coupon.coupon_count=coupon_count
        coupon.expiration_date=expiration_date
        coupon.is_expired=bool(expire_checkbox)  # Convert string to boolean
        
        coupon.save()
        messages.success(request, 'Coupon Edited Successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    return render(request, 'admin_home/admin_edit_coupon.html', context)



@user_passes_test(is_superuser, login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def admin_delete_coupon(request, coupon_uid):
    try:
        coupon = Coupon.objects.get(uid=coupon_uid)
    except Coupon.DoesNotExist:
        raise Http404("Coupon does not exist")  
   
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ---------------------------------BANNER------------------------
@user_passes_test(is_superuser, login_url='admin_login')
def admin_banner(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')





        existing_banner = Banner.objects.filter(title=title).first()

        if not existing_banner:
            banner = Banner.objects.create(title=title)



            if image:
                banner.image.save(image.name, image)

            banner.save()
            messages.success(request, 'Banner saved successfully')
        else:
           messages.warning(request, 'A Banner with same name already exists')
           return redirect('admin_banner')


    banners = Banner.objects.all()
    context = {'banners':banners}
    return render(request, 'admin_home/banner.html', context)



@require_POST
@user_passes_test(is_superuser, login_url='admin_login')
def delete_banner(request):

    data = json.loads(request.body.decode('utf-8'))
    uid = data.get('uid')
     
    banner = get_object_or_404(Banner, uid=uid)

    
    if not request.user.has_perm('your_app.delete_banner'): 
        return JsonResponse({'error': 'Permission Denied'}, status=403)

    banner.delete()
    messages.success(request, 'Banner Deleted successfully')

    return JsonResponse({'success': 'Banner deleted successfully'})






@user_passes_test(is_superuser, login_url='admin_login')
def export_data_to_excel(request):
    objs = OrderItem.objects.all()
    orders = Order.objects.all()
    
    data = []

    for obj in objs:
        data.append({
            "Order ID": obj.order.uid,
            "Item ID": obj.order.uid,
            "Product": obj.product_name,
            "Edition Variant": obj.edition_variant,
            "Quantity": obj.quantity,
            "Price": obj.price,
            "Payment Method": obj.payment_method,
            "Address": f"{obj.street_address}, {obj.city}, {obj.state}, {obj.postal_code}, {obj.country}",
            "Mobile": obj.mobile,
            "Total": obj.get_total(),
            "Paid": obj.is_paid,
            "Order Status": obj.order_status,
        })

    overall_revenue = sum(order.total_amount for order in orders)
    overall_data = {
        "Overall Revenue": overall_revenue,
        
    }

    df_orders = pd.DataFrame(data)
    df_overall = pd.DataFrame([overall_data])

    total_revenue = Order.objects.filter(is_delivered=True).aggregate(Sum('total_amount'))['total_amount__sum']
    total_count = Order.objects.filter(is_delivered = True).count()
    product_count = Product.objects.all().count()
    category_count = Category.objects.all().count()
    if total_count > 0:
        monthly_revenue = total_revenue / total_count
    else:
        monthly_revenue = 0



    if total_revenue is None:
        total_revenue = 0
    if total_count is None:
        total_count = 0
    if product_count is None:
        product_count = 0
    if category_count is None:
        category_count = 0

    overall_combined_data = {
        "Overall Revenue": total_revenue,
        "Total Products Available": product_count,
        "Overall Categories": category_count,
        "Monthly Income": monthly_revenue,
    }


    df_overall_combined = pd.DataFrame([overall_combined_data])

    output_buffer = BytesIO()
    with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
        df_orders.to_excel(writer, sheet_name='Orders', index=False)

        worksheet_orders = writer.sheets['Orders']
        for i, col in enumerate(df_orders.columns):
            max_len = max(df_orders[col].astype(str).apply(len).max(), len(col))
            worksheet_orders.set_column(i, i, max_len)
       

        df_overall_combined = pd.DataFrame([overall_combined_data])
        df_overall_combined.to_excel(writer, sheet_name='Overall',startcol = 2,  index=False)
        start_row_monthly_data = len(df_overall_combined) + 5  
        start_col_monthly_data = len(df_overall_combined.columns) + 2
        df_monthly_data = pd.DataFrame({
            "Months": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            "Sales": [100, 150, 200, 120, 180, 250, 300, 200, 180, 220, 280, 320],
            "Products": [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160],
            "Visitors": [500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600],
        })
        df_monthly_data.to_excel(writer, sheet_name='Overall',  startcol=start_col_monthly_data + 5 , index=False)
        worksheet = writer.sheets['Overall']
        for i, col in enumerate(df_overall_combined.columns):
            max_len = max(df_overall_combined[col].astype(str).apply(len).max(), len(col))
            worksheet.set_column(i + 2, i + 2, max_len) 

        for i, col in enumerate(df_monthly_data.columns):
            max_len = max(df_monthly_data[col].astype(str).apply(len).max(), len(col))
            worksheet.set_column(start_col_monthly_data + i, start_col_monthly_data + i, max_len)  


    output_buffer.seek(0)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=output.xlsx'
    response.write(output_buffer.getvalue())

    return response



