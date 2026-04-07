from django.urls import path
from .views import signup, login_view, me, get_cart_view, update_cart_view, create_order_view, get_products_view, get_orders_view
from .services import create_user_in_mongo

urlpatterns = [
    path('signup/', signup),
    path('login/', login_view),
    path('me/', me),
    path('cart/', get_cart_view),
    path('cart/update/', update_cart_view),
    path('checkout/', create_order_view),
    path('products/', get_products_view),
    path('orders/', get_orders_view),
]