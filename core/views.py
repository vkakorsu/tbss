from django.views.generic import TemplateView
from catalog.models import Book


class HomeView(TemplateView):
    template_name = "core/home.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_books"] = (
            Book.objects.filter(is_active=True, is_featured=True)
            .select_related("publisher")
            .prefetch_related("authors")
            .order_by("title")[:6]
        )
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"
