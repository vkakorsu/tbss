from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "provider", "status", "amount", "created_at")
    list_filter = ("method", "status", "provider")
    search_fields = ("order__order_number", "reference")
    readonly_fields = ("created_at", "updated_at")
