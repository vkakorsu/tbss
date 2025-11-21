from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

from catalog.models import Book
from orders.models import Order
from .models import Review


class ReviewsIndexView(ListView):
    template_name = "reviews/index.html"
    context_object_name = "reviews"
    paginate_by = 20

    def get_queryset(self):
        return Review.objects.select_related("book", "user").filter(is_approved=True)


@login_required
def add_review(request, slug):
    if request.method != "POST":
        return redirect("catalog:detail", slug=slug)
    book = get_object_or_404(Book, slug=slug, is_active=True)
    # verified purchase: user has an order with this book
    verified = Order.objects.filter(user=request.user, items__book=book).exists()
    if not verified:
        messages.error(request, "Only verified customers can review this title.")
        return redirect(book.get_absolute_url())
    rating = request.POST.get("rating")
    title = request.POST.get("title", "").strip()
    body = request.POST.get("body", "").strip()
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError()
    except Exception:
        rating = 5
    Review.objects.update_or_create(
        book=book,
        user=request.user,
        defaults={"rating": rating, "title": title, "body": body, "is_approved": True},
    )
    messages.success(request, "Thanks for reviewing!")
    return redirect(book.get_absolute_url())
