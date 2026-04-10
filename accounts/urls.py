from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login_view),
    path('me/', views.me),
    path('cart/', views.get_cart_view),
    path('cart/update/', views.update_cart_view),
    path('checkout/', views.create_order_view),
    path('products/', views.get_products_view),
    path('orders/', views.get_orders_view),
    path('create-esewa-payment/', views.initiate_esewa_payment, name='esewa_initiate'),
]