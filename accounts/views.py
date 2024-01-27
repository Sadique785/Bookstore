import json
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import authenticate,login, logout
from .models import Profile, Cart, CartItem
from django.contrib.auth.decorators import login_required
from base.emails import generate_otp, send_otp_email
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from products.models import Product, EditionVariant, LanguageVariant
from django.views.decorators.http import require_POST



def login_page(request):
    

    

    if request.user.is_authenticated:
        # If the user is already logged in, check if they are blocked
        if not request.user.is_active:
            # User is blocked, log them out and redirect to the login page
            logout(request)
            messages.warning(request, 'Your account is blocked. Contact the admin for more information.')
            return render(request, 'home/login.html')

        # If the user is authenticated and not blocked, redirect to the home page or any desired URL
        return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)

        if not (email and password):  # Check if email and password are not empty
            messages.warning(request, "Please enter email and password")
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.filter(email=email)
        

        if not user_obj.exists():
            messages.warning(request, "Account Not Found")
            return HttpResponseRedirect(request.path_info)

        user = user_obj.first()
        # if the user who tries to login is inactive then
        if not user.is_active:
            messages.warning(request, "Your account is blocked. Contact the admin for more information.")
            return render(request, 'home/login.html')
        

        if hasattr(user, 'profile'):
            if not user.profile.is_email_verified:
                messages.warning(request, "Your account is not verified")
                return HttpResponseRedirect(request.path_info)
        else:
            messages.warning(request, "User profile not found")
            # Handle this scenario (e.g., redirect or display an error message)

        user_obj = authenticate(username=email, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect('index')
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('login')

    return render(request, 'home/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')



# def forgot_password(request):
#     return render(request, 'accounts/forgot_password.html')

def forgot_password(request):
    if request.method=='POST':
       
        email=request.POST.get('email')
        password=request.POST.get('password')
        otp=request.POST.get('OTP')
        user=User.objects.get(email=email)
        if otp==request.session['otp']:
            hashed_password=make_password(password)
            user.password=hashed_password
            user.save()
            messages.warning(request,'Password reset done. Login with this password.')
            return redirect('forgot_password')
        else:
            messages.warning(request,"OTP doesn't match")
            return redirect('forgot_password')
    return render(request, 'home/forgot_password.html')

def verify(request):
    print('works')
    if request.method=='POST':
        Data=json.loads(request.body)

        email=Data['email']
        if User.objects.filter(email=email).exists():
            otp = generate_otp()
            request.session['otp'] = otp
            send_otp_email(email, otp)
            data={'success':'An OTP is sent to your email'}
            print(data)
            return JsonResponse(data)
        else:
            data={'fail':'Account not found'}
            print(data)
            return JsonResponse(data)

def register_page(request):

     
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email  = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')

        user_obj = User.objects.filter(username = email)
        
        if user_obj.exists():
            messages.warning(request, "Email is already taken")
            return HttpResponseRedirect(request.path_info)
        
        user_obj = User.objects.create(first_name = first_name, last_name = last_name, email = email, username = email )
        user_obj.set_password(password)
        user_obj.save()

        try:
            profile_obj = Profile.objects.get(user=user_obj)
            # Update the existing profile fields
            profile_obj.mobile = mobile
            # Update other fields as needed
            profile_obj.save()
        except Profile.DoesNotExist:
            # If the user does not have a profile, create a new one
            profile_obj = Profile.objects.create(
                user=user_obj,
                mobile=mobile,
                # Add other fields as needed
            )
            profile_obj.save()
        # prof_obj = Profile.objects.create(user = user_obj, mobile = mobile)
        # prof_obj.save()
        messages.success(request, "An email has been sent to your email address")
        return HttpResponseRedirect(request.path_info)
    

    return render(request, 'home/register.html')


def activate_email(request, email_token):
    try:    
        user = Profile.objects.get(email_token = email_token)
        user.is_email_verified = True
        user.save()
        return redirect('index')
        
    except Exception as e:
        return HttpResponse("Invalid Email Token")


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



def remove_cart(request, cart_item_uid):
    try:    
        cart_item = CartItem.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e) 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@require_POST
def change_quantity(request):

    print('Hlo guys')
    # Retrieve the CartItem object
    data  = json.loads(request.body.decode('utf-8'))
    item_uid = data.get('itemUid')
    new_quantity = data.get('newQuantity')

    cart_item = get_object_or_404(CartItem, uid = item_uid)

    cart_item.qty = new_quantity
    cart_item.save()

    new_total = cart_item.get_product_price()
    cart = Cart.objects.get(user = request.user)
    grand_total = cart.get_cart_total()
    return JsonResponse({'success':True, 'newTotal': new_total, 'grand_total':grand_total})



def cart(request):
    cart = Cart.objects.filter(is_paid = False, user = request.user).first()
    cart_items = CartItem.objects.filter(cart = cart)
    print(cart_items)
    print(cart.get_cart_total)

    context = {'cart': cart}
    return render(request, 'accounts/cart.html',context )





# def otp_verification(request):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
#         stored_otp = get_otp_from_session(request)

#         if stored_otp and stored_otp == entered_otp:
#             hashed_password=make_password(request.session['password'])
#             user=User.objects.create(username=request.session['username'],password=hashed_password, email=request.session['email'])
#             profile=Profile.objects.create(user=user,mobile_number=request.session['mob']) 
#             Cart.objects.create(user=user)           
#             request.session['username'] = user.username
#             request.session['email'] = None
#             request.session['password'] = None
#             request.session['mob'] = None
#             return redirect('account:login')
#         else:
#             messages.error(request, 'Invalid OTP. Please try again.')
#             return redirect('account:otp_verification')
#     return render(request, 'account/otp.html')