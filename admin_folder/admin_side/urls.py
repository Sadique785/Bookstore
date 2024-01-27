from django.urls import path, include
from . import views

# app_name = "admin_side"

urlpatterns = [
    path('',views.admin_login, name="admin_login"),
    path('admin_logout',views.admin_logout, name="admin_logout"),
    path('admin_index/',views.admin_index, name="admin_index"),
    path('admin_users/',views.admin_users, name="admin_users"),
    path('details/<int:details_pk>',views.admin_user_details, name="admin_user_details"),
    path('block/<int:block_pk>/', views.block_unblock_user, name='block_unblock_user'),
    path('admin_category/',views.admin_category, name="admin_category"),
    path('admin_category_detail/<slug:slug>/', views.admin_category_detail, name="admin_category_detail"),
    path('admin_subcategory/<slug:slug>', views.admin_subcategory, name="admin_subcategory"),
    path('admin_product/',views.admin_product, name="admin_product"),
    path('admin_product/<slug>',views.admin_product, name="products_by_category"),
    path('admin_add_product/',views.admin_add_product, name="admin_add_product"),
    path('admin_edit_product/<slug:product_slug>',views.admin_edit_product, name="admin_edit_product"),
    path('admin_change_image/', views.admin_change_image, name='admin_change_image'),
    path('unlist_product/<slug:product_slug>',views.unlist_product, name="unlist_product"),
    path('unlist_category/',views.unlist_category, name="unlist_category"),
    path('admin_side/admin_add_product/get_sub_categories/',views.get_sub_categories, name="get_sub_categories"),
    path('admin_variance/',views.admin_variance, name="admin_variance"),
    path('admin_variance_detail/', views.admin_variance_detail, name="admin_variance_detail"),
    path('admin_variance_detail/<uid>/', views.admin_variance_detail, name="admin_variance_detail"),
    # path('admin_variance_detail/<uid>/', views.admin_variance_detail, name="admin_edition_variance_detail"),
    path('admin_edit_variant/<uid>/', views.admin_edit_variant, name="admin_edit_variant"),
    path('delete_variant/<uid>/', views.delete_variant, name="delete_variant"),


    
    # path('get_subcategories/<slug:product_slug>/',views.get_subcategories, name="get_subcategories"),
    # path('get_subcategories/<slug:subcategory_slug>',views.get_subcategories, name="get_subcategories_then"),
    


    # path('select_category/',views.select_category, name='select_category'),
    # path('select_category/<slug>',views.select_category, name='select_category_after')

]