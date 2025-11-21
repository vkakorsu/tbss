from django.urls import path
from .views import (
    AccountHomeView,
    WishlistView,
    add_to_wishlist,
    remove_from_wishlist,
    ProfileView,
    OrdersListView,
    OrderDetailView,
)

app_name = "accounts"

urlpatterns = [
    path("", AccountHomeView.as_view(), name="index"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("orders/", OrdersListView.as_view(), name="orders"),
    path("orders/<str:order_number>/", OrderDetailView.as_view(), name="order_detail"),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/add/<slug:slug>/", add_to_wishlist, name="wishlist_add"),
    path("wishlist/remove/<slug:slug>/", remove_from_wishlist, name="wishlist_remove"),
]
