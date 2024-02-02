
from django.urls import path, include
from . import views
from products import views as products


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
    # path('change-quantity/<str:item_uid>/<int:new_quantity>/', views.change_quantity, name='change_quantity'),
    path('change-quantity/', views.change_quantity, name='change_quantity'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('save_order/', views.save_order, name="save_order"),
    path('cart/checkout/thankyou/', views.thankyou, name="thankyou"),
    path('order_history/', views.order_history, name="order_history"),
    path('order-product-detail/<uid>', views.order_product_detail, name="order_product_detail"),

]



