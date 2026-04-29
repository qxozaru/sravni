from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-price/<int:product_id>/', views.add_price, name='add_price'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/<slug:slug>/', views.store_detail, name='store_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]
