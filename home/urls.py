
from django.urls import path, include
from .import views



# app_name = 'home'


urlpatterns = [
path('', views.index, name="index"),
path('profile/', views.profile_page, name="profile"),
path('manage_address/', views.manage_address, name="manage_address"),
path('add_address/', views.add_address, name="add_address"),
path('edit_address/<str:address_uid>', views.edit_address, name="edit_address"),
path('delete_address/<str:address_uid>', views.delete_address, name="delete_address"),
path('new_address/', views.new_address, name="new_address"),


]