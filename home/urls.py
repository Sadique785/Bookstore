
from django.urls import path, include
from .import views



# app_name = 'home'


urlpatterns = [
path('', views.index, name="index"),
path('contact-us', views.contact_us, name="contact_us"),
path('profile/', views.profile_page, name="profile"),
path('manage-address/', views.manage_address, name="manage_address"),
path('add-address/', views.add_address, name="add_address"),
path('edit-address/<str:address_uid>', views.edit_address, name="edit_address"),
path('delete-address/<str:address_uid>', views.delete_address, name="delete_address"),
path('new-address/', views.new_address, name="new_address"),


]