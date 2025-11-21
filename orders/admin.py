from django.contrib import admin
from .models import ShippingMethod, Order, OrderItem


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "fee", "eta_days_min", "eta_days_max", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "email", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "email", "full_name")
    readonly_fields = ("order_number", "subtotal", "shipping_fee", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
