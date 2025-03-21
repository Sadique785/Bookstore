from audioop import reverse
from django.utils import timezone
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import authenticate,login, logout
from django.conf import settings
from BookStore.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from .models import Invoice, Profile, Cart, CartItem, Wallet, Transaction
from django.contrib.auth.decorators import login_required
from base.emails import generate_otp, send_otp_email
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from products.models import Product, EditionVariant, LanguageVariant, Coupon, ProductVariant
from django.views.decorators.http import require_POST
from home.models import Address, UserAddress
from django.views import View
from django.db import transaction
from orders.models import  Order, OrderAddress, OrderItem
from django.views.decorators.csrf import csrf_exempt
from payments.models import  PaymentMethod
import razorpay
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.db.models import Count, F, Q
from django.core.cache import cache
from django.views.decorators.cache import cache_control



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_page(request):
    

    

    if request.user.is_authenticated:
        if not request.user.is_active:
            logout(request)
            messages.warning(request, 'Your account is blocked. Contact the admin for more information.')
            return render(request, 'home/login.html')

        
        return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)

        if not (email and password): 
            messages.warning(request, "Please enter email and password")
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.filter(email=email)
        

        if not user_obj.exists():
            messages.warning(request, "Account Not Found")
            return HttpResponseRedirect(request.path_info)

        user = user_obj.first()


        if not user.is_active:
            messages.warning(request, "Your account is blocked. Contact the admin for more information.")
            return redirect('login')
        

        if hasattr(user, 'profile'):
            if not user.profile.is_email_verified:
                messages.warning(request, "Your account is not verified")
                return HttpResponseRedirect(request.path_info)
        else:
            messages.warning(request, "User profile not found")
            

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
            del request.session['otp']
            messages.warning(request,'Password reset done. Login with this password.')
            return redirect('forgot_password')
        else:
            messages.warning(request,"OTP doesn't match")
            return redirect('forgot_password')
    return render(request, 'home/forgot_password.html')

def verify(request):
    if request.method=='POST':
        Data=json.loads(request.body)

        email=Data['email']
        if User.objects.filter(email=email).exists():
            otp = generate_otp()
            request.session['otp'] = otp
            send_otp_email(email, otp)
            data={'success':'An OTP is sent to your email'}
            return JsonResponse(data)
        else:
            data={'fail':'Account not found'}
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
            
            profile_obj.mobile = mobile
            
            profile_obj.save()
        except Profile.DoesNotExist:
            profile_obj = Profile.objects.create(
                user=user_obj,
                mobile=mobile,

            )
            profile_obj.save()
       
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
    if not request.user.is_authenticated:
        product = Product.objects.get(uid = uid)
        messages.warning(request, 'Please login to add items to your cart.')
        return redirect('get_product', product.slug)


    variant = request.GET.get('variant')
    print('Variantis',variant)

    product = Product.objects.get(uid = uid)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)
    
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        if variant:
            if cart_item.edition_variant and cart_item.edition_variant.name == variant:
                cart_item.qty += 1
            else:
                edition_variant = EditionVariant.objects.get(name=variant)
                CartItem.objects.create(cart=cart, product=product, edition_variant=edition_variant)
        else:
            cart_item.qty += 1

        cart_item.save()

    else:
        if variant:
            edition_variant = EditionVariant.objects.get(name=variant)
            CartItem.objects.create(cart=cart, product=product, edition_variant=edition_variant)
            messages.success(request, f"{product.product_name} added to cart. Variant: {variant}")

        else:
            messages.success(request, f"{product.product_name} added to cart.")
            CartItem.objects.create(cart=cart, product=product)
            

    if variant:
        messages.success(request, f"{product.product_name} added to cart. Variant: {variant}")
    else:
        messages.success(request, f"{product.product_name} added to cart.")



    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def remove_cart(request, cart_item_uid):
    try:    
        cart_item = CartItem.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




@require_POST
def change_quantity(request):
    data = json.loads(request.body.decode('utf-8'))
    item_uid = data.get('itemUid')
    new_quantity = data.get('newQuantity')

    cart_item = get_object_or_404(CartItem, uid=item_uid)

    cart_item.qty = new_quantity
    cart_item.save()

    new_total = cart_item.get_product_price()
    cart = Cart.objects.get(user=request.user)
    grand_total = cart.get_cart_total()
    grand_subtotal = cart.get_cart_total_couponless()

    coupon_removed = False
    if cart.coupon is not None:
        if grand_total < cart.coupon.minimum_amount:
            cart.coupon = None
            cart.save()
            coupon_removed = True
    else:
        coupon_removed = False

    final_total = cart.get_final_total()
    delivery_charge = cart.delivery_charge if grand_total < 999 else 0

    return JsonResponse({
        'success': True,
        'newTotal': new_total,
        'grand_total': grand_total,
        'grand_subtotal': grand_subtotal,
        'final_total': final_total,
        'delivery_charge': delivery_charge,
        'coupon_removed': coupon_removed
    })



@login_required
def cart(request):
    cart = Cart.objects.filter(is_paid=False, user=request.user).first()

    if request.method == "POST":
        coupon_code = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon_code).first()

        if not coupon_obj:
            messages.warning(request, 'Invalid Coupon')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart.coupon:
            messages.warning(request, 'Coupon already Exists. Remove it to apply new one')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart in coupon_obj.carts_used.all():
            messages.warning(request, 'This coupon has already been applied to your cart.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        



        if cart.get_cart_total() <= coupon_obj.minimum_amount:
            messages.warning(request, f'Amount should be greater than {coupon_obj.minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if coupon_obj.is_expired:
            messages.warning(request, 'Coupon is Expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart.coupon = coupon_obj
        cart.save()
        messages.success(request, 'Coupon Applied')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if cart:
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            print(item.product.product_name)
    else:
        cart_items = []

    context = {'cart': cart, 'cart_items': cart_items}
    return render(request, 'accounts/cart.html', context)




def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid=cart_id)

    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon Removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




@login_required
def order_history(request):
    orders = Order.objects.annotate(
        unpaid_order_items_count=Count('order_items', filter=~Q(order_items__is_paid=True))
    ).order_by('-created_at')

    paid_orders = orders.filter(unpaid_order_items_count=0, is_paid=True, user=request.user)
    failed_orders = orders.exclude(unpaid_order_items_count=0, is_paid=True).filter(user=request.user)

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        selected_value = data.get('selectedValue')

        if selected_value == 'all':
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
        elif selected_value == 'paid':
            orders = paid_orders.filter(user=request.user).order_by('-created_at')
        elif selected_value == 'nonpaid':
            orders = failed_orders.filter(user=request.user).order_by('-created_at')
        else:
            return JsonResponse({'error': 'Invalid filter selected'})

        orders_data = []
        for order in orders:
            order_items = order.order_items.all()
            for item in order_items:
               
                pass

            order_dict = {
                'order': order.to_dict(),
                'order_items': [item.to_dict() for item in order_items],
            }
            orders_data.append(order_dict)

        response_data = {'orders': orders_data}
        return JsonResponse(response_data)

    context = {'orders': paid_orders}
    return render(request, 'accounts/order_history.html', context)




def order_product_detail(request, uid):
    item = OrderItem.objects.get(uid = uid)
    item_price = float(item.price)*item.quantity
    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))

    DATA = {
        "amount": item_price * 100,
        "currency": "INR",
        
        
    }
    payment_order = client.order.create(data=DATA)
    payment_order_id = payment_order['id']    
    
    context = {'item':item,
               'api_key':RAZORPAY_API_KEY,
                'order_id':payment_order_id,
                'callback_url':settings.CALLBACK_URL,
                }


    return render(request, 'accounts/order_product_detail.html', context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
@login_required
def checkout(request):
    print('entered')
    print(settings.CALLBACK_URL)
    user = request.user
    user_addresses = UserAddress.objects.filter(user=user)
    addresses = [user_address.address for user_address in user_addresses]

    default_address = UserAddress.objects.filter(is_default=True).first()
    cart = Cart.objects.filter(is_paid=False, user=user).first()
    cart_items = CartItem.objects.filter(cart=cart, product__stock_quantity__gt=0)
    cart_total = cart.get_cart_total()
    final_total = cart.get_final_total()

    payment_methods = PaymentMethod.objects.filter(is_active=True)

    online_payment = PaymentMethod.objects.filter(name='Online Payment').first()
    online_payment_uid = online_payment.uid

    cash_on_delivery = PaymentMethod.objects.filter(name='Cash On Delivery').first()
    cash_on_delivery_uid = cash_on_delivery.uid

    wallet_payment = PaymentMethod.objects.filter(name='Wallet Payment').first()
    wallet_payment_uid = wallet_payment.uid

    wallet = Wallet.objects.filter(user=user).first()
    wallet_balance = wallet.balance if wallet else 0

    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
    data = {"amount": final_total * 100, "currency": "INR"}
    payment_order = client.order.create(data=data)
    payment_order_id = payment_order['id']

    context = {
        "addresses": addresses,
        "default_address": default_address,
        "order_items": cart_items,
        "cart_total": cart_total,
        'payment_methods': payment_methods,
        'cart_uid': cart.uid,
        'api_key': RAZORPAY_API_KEY,
        'order_id': payment_order_id,
        'callback_url': settings.CALLBACK_URL,
        'online_payment_uid': online_payment_uid,
        'wallet_payment_uid': wallet_payment_uid,
        'cash_on_delivery_uid': cash_on_delivery_uid,
        'final_total': final_total,
        'cart': cart,
        'wallet_balance': wallet_balance
    }
    return render(request, 'accounts/checkout.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
@require_POST
def save_order(request):
    user = request.user

    data = json.loads(request.body.decode('utf-8'))
    addressUid = data.get('addressUid')
    paymentUid = data.get('paymentUid')
    cartItemUid = data.get('cartItemUid')

    address = Address.objects.get(uid=addressUid)
    payment_method = PaymentMethod.objects.filter(uid=paymentUid).first()
    cart = Cart.objects.get(uid=cartItemUid)

    if payment_method.name == 'Wallet Payment':
        wallet = Wallet.objects.filter(user=user).first()
        if wallet:
            wallet_balance = wallet.balance
            if cart.get_final_total() > wallet_balance:
                return JsonResponse({'status': 'error', 'message': 'Insufficient wallet balance.', 'redirect_url': 'checkout'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Insufficient wallet balance.', 'redirect_url': 'checkout'})

    if cart.coupon:
        coupon_code = cart.coupon
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon_code).first()
        coupon_obj.carts_used.add(cart)
        coupon_obj.coupon_count -= 1
        coupon_obj.save()
        cart.coupon = None
        cart.save()

    cart_items = CartItem.objects.filter(cart=cart, product__stock_quantity__gt=0)
    all_cart_items = CartItem.objects.filter(cart=cart)

    order = Order.objects.create(
        user=request.user,
        order_status=Order.PROCESSING,
        total_amount=cart.get_final_total(),
    )
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
            language_variant=language_variant,
            edition_variant=edition_variant,
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
        if cart_item.edition_variant:
            product_variant = ProductVariant.objects.filter(product=cart_item.product, variant=cart_item.edition_variant).first()
            if product_variant:
                product_variant.stock_quantity -= cart_item.qty
                product_variant.save()
        else:
            curr_product = Product.objects.filter(product_name=cart_item.product.product_name).first()
            if curr_product:
                curr_product.stock_quantity = max(0, curr_product.stock_quantity - cart_item.qty)
                curr_product.save()
            else:
                print(f"Product with name {cart_item.product.product_name} not found.")



    total_amount = cart.get_final_total()
    if payment_method.name == 'Wallet Payment':
        wallet_balance = Wallet.objects.filter(user=user).update(balance=F('balance') - total_amount)
        wallet = Wallet.objects.filter(user=user).first()
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=total_amount,
            transaction_type='debit',
            description='Removed money from wallet',
        )
        transaction.save()

    all_cart_items.delete()

    data = {
        'status': 'success',
        'message': 'Order saved successfully',
        'order_id': '12345',  # Replace with the actual order ID or relevant data
    }

    return JsonResponse(data)



@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
@csrf_exempt
def razorpay_callback(request):
    if request.method == 'POST':
        try:
            razorpay_order_id = request.POST.get('razorpay_order_id')
            payment_id = request.POST.get('razorpay_payment_id')
            signature = request.POST.get('razorpay_signature')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
            result = client.utility.verify_payment_signature(params_dict)

            if result is not None:
                return redirect('thankyou')
            else:
                try:
                    last_order = Order.objects.latest('created_at')
                    messages.error(request, 'Payment failed. Order deleted.')
                except Order.DoesNotExist:
                    messages.error(request, 'Payment failed. Order not found.')
                return redirect('checkout')
        except:
            try:
                last_order = Order.objects.latest('created_at')
                last_order.is_paid = False
                last_order.order_status = 'PENDING'
                last_order.save()

                last_order_items = OrderItem.objects.filter(order=last_order)
                last_order_items.update(is_paid=False)
                last_order_items.update(order_status='PENDING')

                messages.warning(request, 'Payment failed. Please try again.')
            except Order.DoesNotExist:
                messages.warning(request, 'Payment failed. Order not found.')
            return render(request, 'accounts/failed_payment.html')

    return render(request, 'accounts/demo.html')






def thankyou(request):
    user = request.user
    cart = Cart.objects.filter(user = user).first()
    all_cart_items  = CartItem.objects.filter(cart = cart)
    all_cart_items.delete()
    return render(request, 'home/thankyou.html')


@csrf_exempt
@login_required
def wallet(request):
    user = request.user
    user_id = user.id
    context = {
        'user_id': user_id,
        'callback_url': settings.CALLBACK_URL, 
    }
    wallet = Wallet.objects.filter(user = user).first()
    if wallet:
        context['balance'] = wallet.balance
        context['refund'] = wallet.refund
        context['wallet'] = wallet.balance - wallet.refund
    else:
        context['balance'] = 0
        context['refund'] = 0
        context['wallet'] = 0
        
    return render(request, 'accounts/wallet.html', context)

@csrf_exempt
@login_required
def create_razorpay_order(request):
    if request.method == 'POST':
        data = request.POST.get('amount')
        amount = int(data)
        client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))

        razorpay_order = client.order.create(data={
            'amount': amount * 100,
            'currency': 'INR',
        })
        api_key = RAZORPAY_API_KEY

        order_id = razorpay_order['id']

        response_data = {
            'order_id': order_id,
            'api_key': api_key,
            'callback_url': settings.CALLBACK_URL,

        }
        return JsonResponse(response_data)




@csrf_exempt
def add_money(request):
    amount = request.GET.get('amount')
    user_id = request.GET.get('userid')

    if request.method == 'POST':
        try:
            razorpay_order_id = request.POST.get('razorpay_order_id')
            payment_id = request.POST.get('razorpay_payment_id')
            signature = request.POST.get('razorpay_signature')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
            result = client.utility.verify_payment_signature(params_dict)

        except:
            messages.warning(request, 'Payment Failed. Please Try again')
            return redirect('wallet')

        if result:
            amount = Decimal(amount)
            user = User.objects.filter(id=user_id).first()
            wallet = Wallet.objects.filter(user=user).first()

            if wallet:
                wallet.balance += amount
                wallet.save()
                transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='credit',
                    description='Added money to wallet',
                )
                transaction.save()
                messages.success(request, 'Money added successfully')

                return redirect('wallet')

            else:
                wallet = Wallet.objects.create(user=user, balance=amount)
                wallet.save()
                transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='credit',
                    description='Added money to wallet',
                )
                transaction.save()
                messages.success(request, 'Money added successfully')
                return redirect('wallet')

    return redirect('wallet')




@login_required
def transactions(request):

    try:
        user = request.user
        wallet = Wallet.objects.filter(user=user).first()

        if wallet:
            transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        else:
            transactions = []

        context = {'transactions': transactions}

    except Exception as e:
        print(f"An error occurred: {e}")
        context = {'transactions': []}

    return render(request, 'accounts/transactions.html', context)



@login_required
def coupons(request):
    try:
        user_cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.warning(request, 'You Dont have a cart. Redirected to the Profile')
        return redirect('profile')  

    all_coupons = Coupon.objects.all()
    available_coupons = []

    for coupon in all_coupons:
        if user_cart not in coupon.carts_used.all():
            available_coupons.append(coupon)

    context = {'coupons': available_coupons}
    return render(request, 'accounts/coupons.html', context)


@require_POST
def cancel_item(request):
    try:
        data = json.loads(request.body)
        item_uid = data.get('item_uid')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})

    order_item = get_object_or_404(OrderItem, uid=item_uid)

    if order_item.is_active:
        
        user = request.user
        wallet = Wallet.objects.filter(user=user).first()
        if wallet:
            wallet.balance += order_item.get_total()
            wallet.refund += order_item.get_total()
            wallet.save()
            transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=order_item.get_total(),
                    transaction_type='credit',
                    description='Added money to wallet',
                )
            transaction.save()
        else:
            wallet = Wallet.objects.create(user=user, balance=order_item.get_total())
            wallet.save()
            transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=order_item.get_total(),
                    transaction_type='credit',
                    description='Added money to wallet',
                )
            transaction.save()
            
        order_item.is_active = False
        order_item.save()

        order_item.order.total_amount -= order_item.get_total()
        order_item.order.save()

        all_orders = order_item.order.order_items.all()
        all_items_cancelled = all(not order.is_active for order in all_orders)

        if all_items_cancelled:
            order_item.order.is_active = False
            order_item.order.save()


        order_item.order_status = None  
        order_item.save()

        if order_item.edition_variant:
            product = Product.objects.filter(product_name = order_item.product_name).first()
            product_variant = ProductVariant.objects.all()
            edition_variant = EditionVariant.objects.filter(name = order_item.edition_variant).first()
            product_variant = ProductVariant.objects.filter(product = product, variant = edition_variant).first()
            product_variant.stock_quantity += order_item.quantity
            product_variant.save()
            
        else:

            product = Product.objects.filter(product_name = order_item.product_name).first()
            product.stock_quantity += order_item.quantity
            product.save()
            

        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=order_item.get_total(),
            transaction_type='credit',
            description='Added money to wallet',
        )
        transaction.save()

        response_data = {'success': True, 'message': 'Order item successfully cancelled'}
    else:
        response_data = {'success': False, 'message': 'Order item is already cancelled'}

    return JsonResponse(response_data)



@csrf_exempt
def failed_payment(request):
    uid = request.GET.get('uid')
    order_item = OrderItem.objects.filter(uid=uid).first()

    if request.method == 'POST':
        try:
            razorpay_order_id = request.POST.get('razorpay_order_id')
            payment_id = request.POST.get('razorpay_payment_id')
            signature = request.POST.get('razorpay_signature')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
            result = client.utility.verify_payment_signature(params_dict)

            if result:
                order_item.is_paid = True
                order_item.order_status = 'PROCESSING'
                order_item.save()

            orders = order_item.order.order_items.all()
            all_items_paid = all(order.is_paid for order in orders)

            if all_items_paid:
                order_item.order.is_paid = True
                order_item.order.save()

            messages.success(request, 'Payment Completed')

        except:
            messages.warning(request, 'Payment Failed Please Try again')
            return redirect('order_product_detail',uid)

    return redirect('order_product_detail', uid)



def invoice(request, item_uid):
    

    order_item = OrderItem.objects.filter(uid = item_uid).first()
    invoice_date = timezone.now()
    

    
    context = {
        'order_item':order_item,
        'invoice_date':invoice_date,
        
    }
    return render(request, 'accounts/invoice.html',context)



def email_verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if User.objects.filter(email=email).exists():
            otp = generate_otp()
            request.session['otp'] = otp
            send_otp_email(email, otp)
            return JsonResponse({'success': 'An OTP is sent to your email'})
        else:
            return JsonResponse({'fail': 'Account not found'})
        
def confirm_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp = data.get('otp')

        if not otp:
            return JsonResponse({'error': 'OTP cannot be empty'}, status=400)
        
        if len(otp) != 6:
            return JsonResponse({'error': 'OTP must be exactly 6 characters long'}, status=400)

        
        if otp == request.session.get('otp'):
            
            del request.session['otp']
            return JsonResponse({'success': 'Email confirmed'})
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)