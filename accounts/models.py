from django.conf import settings
from django.db import models
from django.utils import timezone
from catalog.models import Book


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=40, blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile({self.user})"


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist"
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Wishlist({self.user})"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="wishlisted_in"
    )
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("wishlist", "book")

    def __str__(self):
        return f"{self.book.title}"
