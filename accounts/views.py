from audioop import reverse
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
from home.models import Address, UserAddress
from django.views import View
from django.db import transaction
from orders.models import  Order, OrderAddress, OrderItem
from django.views.decorators.csrf import csrf_exempt
from payments.models import  PaymentMethod





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
        messages.success(request, 'Successfully registered Please Login')
        return redirect('login')
        
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
    # Retrieve the cart for the user
    cart = Cart.objects.filter(is_paid=False, user=request.user).first()
    
    if cart:
        cart_items = CartItem.objects.filter(cart=cart)
        print(cart_items)
        print(cart.get_cart_total)
    else:
        cart_items = []

    context = {'cart': cart, 'cart_items': cart_items}
    return render(request, 'accounts/cart.html', context)



def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # order_items_dict = {}

    # for order in orders:
    #     order_items = OrderItem.objects.filter(order=order)
    #     order_items_dict[order] = order_items

    # context = {'orders': orders, 'order_items_dict': order_items_dict}
    context = {'orders':orders}
    return render(request, 'accounts/order_history.html', context)


def order_product_detail(request, uid):
    item = OrderItem.objects.get(uid = uid)
    context = {'item':item}
    return render(request, 'accounts/order_product_detail.html', context)






@login_required
def checkout(request):
    user = request.user
    user_addresses = UserAddress.objects.filter(user=user)
    addresses = [user_address.address for user_address in user_addresses]

    # default_address = next((user_address.address for user_address in user_addresses if user_address.is_default), None)
    default_address = UserAddress.objects.filter(is_default = True).first()
    print(default_address)
    cart = Cart.objects.filter(is_paid=False, user=user).first()
    cart_items = CartItem.objects.filter(cart=cart)
    cart_total = cart.get_cart_total()
    payment_methods = PaymentMethod.objects.filter(is_active=True)

    context = {
        "addresses": addresses,
        "default_address": default_address,
        "order_items": cart_items,
        "cart_total": cart_total,
        'payment_methods':payment_methods,
        'cart_uid':cart.uid,
         
    }
    return render(request, 'accounts/checkout.html', context)


@require_POST
def save_order(request):
    user = request.user

    data  = json.loads(request.body.decode('utf-8'))
    print(data)
    addressUid = data.get('addressUid')
    paymentUid = data.get('paymentUid')
    cartItemUid = data.get('cartItemUid')

    address = Address.objects.get(uid = addressUid)
    print(address)
    payment_method = PaymentMethod.objects.get(uid = paymentUid)
    print(payment_method)
    cart = Cart.objects.get(uid = cartItemUid)
    print(cart)
    cart_items  = CartItem.objects.filter(cart = cart)
    print(cart)

    order = Order.objects.create(
    user=request.user,  # Assuming you have user authentication
    order_status=Order.PENDING,
    total_amount=cart.get_cart_total(),
    )
    print(order)
    order.save()

            

    for cart_item in cart_items:
        first_image = cart_item.product.product_images.first()
        if cart_item.edition_variant:
            edition_variant = cart_item.edition_variant.name
        else:
            edition_variant = None

        if cart_item.language_variant:
            language_variant = cart_item.language_variant.name

        else:
            language_variant = None
       

        order_item = OrderItem.objects.create(
            order=order,
            product_name=cart_item.product.product_name,
            quantity=cart_item.qty,
            language_variant = language_variant,
            edition_variant = edition_variant,
            price=cart_item.product.price,
            payment_method=payment_method,
            image=first_image.image if first_image else None,
            name=address.name,
            city=address.city,
            country=address.country,
            state=address.state,
            postal_code=address.postal_code,
            street_address=address.street_address,
            mobile=address.mobile,
        )
        order_item.save()
        print(order_item)
        

        cart_items.delete()
        






    # Your logic to save the order goes here

    # Assuming you have some data to return in the JSON response
    data = {
        'status': 'success',
        'message': 'Order saved successfully',
        'order_id': '12345',  # Replace with the actual order ID or relevant data
    }

    return JsonResponse(data)


def thankyou(request):
    return render(request, 'home/thankyou.html')

# @require_POST
# def save_order_address(request):
#     url = reverse('save_order_address')
#     print(f'URL: {url}')
#     try:
#         data = json.loads(request.body.decode('utf-8'))
#         selected_address_uid = data.get('selected_address_uid')
#         selected_address = Address.objects.get(uid=selected_address_uid)

#         order_instance = Order.objects.create(
#             user=request.user,
#             total_amount=0,
#         )
#         order_instance.save()

#         order_address = OrderAddress.objects.create(
#             order=order_instance,
#             name=selected_address.name,
#             city=selected_address.city,
#             country=selected_address.country,
#             state=selected_address.state,
#             postal_code=selected_address.postal_code,
#             street_address=selected_address.street_address,
#             mobile=selected_address.mobile,
#             is_billing_address=False,
#             is_shipping_address=False,
#         )

#         return JsonResponse({
#             'order_uid': order_instance.uid,
#             'selected_address_uid': selected_address_uid,
#         })

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
            


# class SaveOrderAddressView(View):
#     print('First')
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body.decode('utf-8'))

#             selected_address_uid = data.get('selected_address_uid')

            
#             selected_address = Address.objects.get(uid=selected_address_uid)
#             print(selected_address)
#             print('second')
#             # Start a database transaction
#             with transaction.atomic():
#                 order_address = OrderAddress(
#                     name=selected_address.name,
#                     city=selected_address.city,
#                     country=selected_address.country,
#                     state=selected_address.state,
#                     postal_code=selected_address.postal_code,
#                     street_address=selected_address.street_address,
#                     mobile=selected_address.mobile,
                    
#                     is_billing_address=False,
#                     is_shipping_address=False,
#                 )
#                 order_address.save()

#                 order_instance = Order(
#                     user=request.user,
#                     total_amount=0,
#                 )
#                 print(order_instance)
#                 order_instance.save()

#                 order_address.order = order_instance
#                 order_address.save()



#                 transaction.on_commit(lambda: self.handle_transaction_success(order_instance, selected_address_uid))

#             return JsonResponse({'order_uid': order_instance.uid, 'selected_address_uid': selected_address_uid, })

#         except Exception as e:
#             print('error')
#             print(f"Error: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)


#     def handle_transaction_success(self, order_instance, selected_address_uid):
#         print(f"Order {order_instance.uid} created successfully.")
#         print(f"Selected address with UID {selected_address_uid} processed successfully.")

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