from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='index'),
    path('login/', views.login, name='login'),
    path('logout',views.logout,name='logout'),
    path('register/', views.register, name='register'),
    path('checkout/', views.checkout, name='checkout'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:id>/', views.add_to_cart,name="add_to_cart"),
    path('cart/adjust/<int:id>/', views.adjust_cart, name="adjust_cart"),
    path('cart/remove/<int:id>/',views.remove_item, name="remove_item"),
    path('checkout/done/',views.purchase_complete, name="purchase_complete")
]