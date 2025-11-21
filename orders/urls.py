from django.urls import path
from .views import CartView, add_to_cart, remove_from_cart, clear_cart, decrease_quantity, CheckoutView, OrderSuccessView

app_name = "orders"

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/<slug:slug>/", add_to_cart, name="cart_add"),
    path("cart/dec/<slug:slug>/", decrease_quantity, name="cart_dec"),
    path("cart/remove/<slug:slug>/", remove_from_cart, name="cart_remove"),
    path("cart/clear/", clear_cart, name="cart_clear"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("success/<str:order_number>/", OrderSuccessView.as_view(), name="success"),
]
