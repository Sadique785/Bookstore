from django.urls import path, include
from . import views


urlpatterns = [
   path('',views.all_products, name="all_products"),
   path('category/<slug:category_slug>/',views.all_products, name="all_products_bycat"),
   path('product/<slug:product_slug>/',views.get_product, name="get_product"),

]