from django.contrib import admin
from .models import Profile, Wishlist, WishlistItem


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "region")
    search_fields = ("user__username", "user__email", "phone")


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    inlines = [WishlistItemInline]
