from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from catalog.models import Book
from .models import Wishlist, WishlistItem, Profile
from orders.models import Order


@method_decorator(login_required, name="dispatch")
class AccountHomeView(TemplateView):
    template_name = "accounts/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        orders = Order.objects.filter(user=self.request.user).order_by("-created_at")
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        ctx.update(
            {
                "profile": profile,
                "orders": orders[:3],
                "orders_count": orders.count(),
                "wishlist": wishlist,
                "wishlist_count": wishlist.items.count(),
            }
        )
        return ctx


@method_decorator(login_required, name="dispatch")
class WishlistView(TemplateView):
    template_name = "accounts/wishlist.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        wishlist = (
            Wishlist.objects.filter(pk=wishlist.pk)
            .prefetch_related("items__book__authors")
            .first()
        )
        ctx["wishlist"] = wishlist
        return ctx


@login_required
def add_to_wishlist(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    WishlistItem.objects.get_or_create(wishlist=wishlist, book=book)
    messages.success(request, f"Added to wishlist: {book.title}")
    return redirect(book.get_absolute_url())


@login_required
def remove_from_wishlist(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    WishlistItem.objects.filter(wishlist=wishlist, book=book).delete()
    messages.info(request, f"Removed from wishlist: {book.title}")
    return redirect("accounts:wishlist")


@method_decorator(login_required, name="dispatch")
class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.phone = request.POST.get("phone", "")
        profile.address_line1 = request.POST.get("address_line1", "")
        profile.address_line2 = request.POST.get("address_line2", "")
        profile.city = request.POST.get("city", "")
        profile.region = request.POST.get("region", "")
        profile.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        ctx["profile"] = profile
        return ctx


@method_decorator(login_required, name="dispatch")
class OrdersListView(TemplateView):
    template_name = "accounts/orders.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = Order.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
        return ctx


@method_decorator(login_required, name="dispatch")
class OrderDetailView(TemplateView):
    template_name = "accounts/order_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order_number = self.kwargs.get("order_number")
        order = get_object_or_404(
            Order, order_number=order_number, user=self.request.user
        )
        ctx["order"] = order
        return ctx
