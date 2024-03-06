from django.shortcuts import render,redirect
from products.models import Product
from django.contrib.auth.models import User
from accounts.models import Profile 
from .forms import InfoFirst, InfoSecond, InfoThird, ManageAddress
from django.contrib import messages
from .models import Address, UserAddress
from django.shortcuts import get_object_or_404
from .constants import COUNTRY_CHOICES
from django.contrib.auth.decorators import login_required
from home.models import Banner




# Create your views here.


def index(request):
    products = Product.objects.filter(is_listed = True, is_category_listed = True)
    new_products = Product.objects.filter(is_listed = True, is_category_listed = True).order_by('-created_at')
    banners = Banner.objects.all().order_by('-created_at')
    if banners.count() >= 3:
        banners = Banner.objects.all().order_by('-created_at')[:3]

    else:
        banners = Banner.objects.all().order_by('-created_at')


   


    context = {
        'products': products,
        'new_products':new_products,
        'banners':banners,
        }
    
    return render(request, 'home/real_index.html', context)

@login_required
def profile_page(request):
    user = request.user
    profile = Profile.objects.get(user = user)

    form_first = InfoFirst(instance=user)
    form_second = InfoSecond(instance=user)
    form_third = InfoThird(instance=profile)


    context = {
        'profile':profile,
        'user':user,
        'form_first': form_first,
        'form_second': form_second,
        'form_third': form_third,
    }


    if request.method =='POST':
        form_type = request.POST.get('form_type')

        if form_type == 'personal_info':
            form = InfoFirst(request.POST, instance=user)

        elif form_type == 'email':
            form = InfoSecond(request.POST, instance=user)

        elif form_type == 'mobile':
            form = InfoThird(request.POST, instance=profile)

        else:
            messages.error(request, 'Invalid form type.')
            return redirect('profile')
        
        if form.is_valid():
            form.save()


            # if not form.is_valid():
            #     messages.warning(request, 'Form submission failed. Please check the form data.')
            #     context['form_errors'] = form.errors
            #     return render(request, 'home/profile_page.html', context)
            
            
            messages.success(request, f'{form_type.capitalize()}  saved successfully.')
            return redirect('profile')
        else:
            messages.warning(request, 'Form submission failed. Please check the form data.')
            
            context['form_errors'] = form.errors  # Correct indentation
            return render(request, 'home/profile_page.html', context)
        


    return render(request, 'home/profile_page.html', context)

@login_required
def manage_address(request):
    # form = ManageAddress()
    user = request.user
    user_addresses = UserAddress.objects.filter(user=user)
    other_addresses =UserAddress.objects.filter(user=user).exclude(is_default = True)
    addresses = [user_address.address for user_address in other_addresses]
    default_address = user_addresses.filter(is_default=True).first()

    context = {"addresses": addresses,
               "default_address": default_address,
               }
    return render(request, 'home/manage_address.html', context)


@login_required
def add_address(request):
    context = {}
    if request.method == 'POST':
        form = ManageAddress(request.POST)

        if form.is_valid():
            address = form.save()

            is_default=form.cleaned_data.get('is_default', False)


            user_address = UserAddress(
                user=request.user,
                address=address,
                is_default=is_default # Set is_default based on the form data
            )
            user_address.save()

            if is_default:
                UserAddress.objects.filter(user=request.user).exclude(uid=user_address.uid).update(is_default=False)


            messages.success(request, 'Address added successfully.')
            return redirect('manage_address')
        else:
            messages.warning(request, 'Form submission failed. Please check the form data.')
            context['form'] = form
            context['form_errors'] = form.errors
            
        
    else:
        form = ManageAddress() 
        context = {"form":form}
    
    
    return render(request, 'home/add_address.html', context)


@login_required
def new_address(request):
    context = {}
    if request.method == 'POST':
        form = ManageAddress(request.POST)

        if form.is_valid():
            address = form.save()

            is_default=form.cleaned_data.get('is_default', False)


            user_address = UserAddress(
                user=request.user,
                address=address,
                is_default=is_default 
            )
            user_address.save()

            if is_default:
                UserAddress.objects.filter(user=request.user).exclude(uid=user_address.uid).update(is_default=False)


            messages.success(request, 'Address added successfully.')
            return redirect('checkout')
        else:
            messages.warning(request, 'Form submission failed. Please check the form data.')
            context['form'] = form
            context['form_errors'] = form.errors
            
        
    else:
        form = ManageAddress() 
        context = {"form":form}
    
    
    return render(request, 'home/new_address.html', context)


@login_required
def edit_address(request, address_uid):
    user = request.user
    # print(user)
    # print(address_uid)
    user_address = UserAddress.objects.get(address = address_uid )

    address = user_address.address 
    is_default = user_address.is_default

    if request.method == 'POST':
        form = ManageAddress(request.POST, instance=address)

        if form.is_valid():
            updated_address = form.save()


            is_default_updated = form.cleaned_data.get('is_default', False)
            if is_default_updated:
                UserAddress.objects.filter(user=user).exclude(uid=user_address.uid).update(is_default=False)


            user_address.address = updated_address
            user_address.is_default = is_default_updated
            user_address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('edit_address',address_uid = address_uid )
        else:
            messages.warning(request, 'Form submission failed. Please check the form data.')
    
    else:
        form = ManageAddress(instance=address, initial={'is_default': is_default})

    
    context = {
        "form": form,
        "address_uid": address_uid,
        "country_choices": COUNTRY_CHOICES,
    }

    return render(request, 'home/edit_address.html', context)





@login_required
def delete_address(request, address_uid):
    address = get_object_or_404(Address, uid = address_uid)
    user_address = UserAddress.objects.filter(user = request.user, address = address )

    if not user_address:
        return redirect('manage_address')
    
    user_address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('manage_address')


@login_required
def contact_us(request):
    user = request.user
    profile = Profile.objects.filter(user = user).first()
    user_addresses = UserAddress.objects.filter(user=request.user)
    context = {'user':user,
               'profile':profile,
               'user_addresses':user_addresses,}
    return render(request, 'home/contact_us.html', context)
