from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from catalog.models import Book


class ShippingMethod(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    eta_days_min = models.PositiveIntegerField(default=2)
    eta_days_max = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["fee", "name"]

    def __str__(self):
        return f"{self.name} (GH₵ {self.fee})"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("new", "New"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    order_number = models.CharField(max_length=20, unique=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")

    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=40)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.PROTECT, related_name="orders")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default="new")

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} x {self.quantity}"
