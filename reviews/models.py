from django.conf import settings
from django.db import models
from django.utils import timezone
from catalog.models import Book


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("book", "user")

    def __str__(self):
        return f"{self.book.title} review by {self.user}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update book aggregate rating
        agg = self.book.reviews.filter(is_approved=True).aggregate(avg=models.Avg("rating"))
        avg = agg.get("avg") or 0
        if self.book.rating != float(avg):
            self.book.rating = float(avg)
            self.book.save(update_fields=["rating"])
