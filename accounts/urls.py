
from django.urls import path, include
from . import views

urlpatterns = [
    path('login/',views.login_page, name="login"),
    path('register/',views.register_page, name="register"),
    path('activate/<email_token>',views.activate_email, name="activate_email"),
    path('forgot_password/',views.forgot_password, name="forgot_password"),
    path('verify/',views.verify, name='verify'),
    path('logout/',views.user_logout, name="logout"),
    
]