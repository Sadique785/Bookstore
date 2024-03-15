
from django.urls import path, include
from . import views


urlpatterns = [
    path('login/',views.login_page, name="login"),
    path('register/',views.register_page, name="register"),
    path('activate/<email_token>',views.activate_email, name="activate_email"),
    path('forgot_password/',views.forgot_password, name="forgot_password"),
    path('verify/',views.verify, name='verify'),
    path('logout/',views.user_logout, name="logout"),
    path('cart/', views.cart, name="cart"),
    path('add-to-cart/<uid>',views.add_to_cart, name="add_to_cart"),
    path('remove-cart/<cart_item_uid>',views.remove_cart, name="remove_cart"),
    path('change-quantity/', views.change_quantity, name='change_quantity'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('save_order/', views.save_order, name="save_order"),
    path('cart/checkout/thankyou/', views.thankyou, name="thankyou"),
    path('order_history/', views.order_history, name="order_history"),
    path('order-product-detail/<uid>', views.order_product_detail, name="order_product_detail"),
    path('order_product_detail/<uuid:uid>/', views.order_product_detail, name='order_new_product_detail'),
    path('remove-coupon/<cart_id>', views.remove_coupon, name="remove_coupon"),
    path('payment-callback/', views.razorpay_callback, name='razorpay_callback'),
    path('failed-payment/', views.failed_payment, name='failed_payment'),
    path('wallet/', views.wallet, name='wallet'),
    path('transactions/', views.transactions, name='transactions'),
    path('coupons/', views.coupons, name='coupons'),
    path('add-money/', views.add_money, name='add_money'),
    path('create_razorpay_order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('cancel_item/', views.cancel_item, name='cancel_item'),
    path('invoice/<item_uid>', views.invoice, name='invoice'),
    path('email_verify/', views.email_verify, name='email_verify'),
    path('confirm_email/', views.confirm_email, name='confirm_email'),


    
]



