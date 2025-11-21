from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, View
from .models import Book, Author, Genre
try:
    from rapidfuzz import process, fuzz  # type: ignore
    HAS_FUZZ = True
except Exception:  # pragma: no cover
    process = None  # type: ignore
    fuzz = None  # type: ignore
    HAS_FUZZ = False


class CatalogListView(ListView):
    model = Book
    context_object_name = "books"
    paginate_by = 12
    template_name = "catalog/index.html"

    def get_queryset(self):
        qs = Book.objects.select_related("publisher").prefetch_related("authors", "genres", "tags").filter(is_active=True)
        q = self.request.GET.get("q", "").strip()
        genre = self.request.GET.get("genre")
        author = self.request.GET.get("author")
        price_min = self.request.GET.get("min")
        price_max = self.request.GET.get("max")
        availability = self.request.GET.get("avail")

        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(isbn__icontains=q)
                | Q(description__icontains=q)
                | Q(authors__name__icontains=q)
                | Q(tags__name__icontains=q)
            ).distinct()

        if genre:
            qs = qs.filter(genres__slug=genre)
        if author:
            qs = qs.filter(authors__slug=author)
        if price_min:
            try:
                qs = qs.filter(price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                qs = qs.filter(price__lte=float(price_max))
            except ValueError:
                pass
        if availability == "in":
            qs = qs.filter(stock__gt=0)
        elif availability == "out":
            qs = qs.filter(stock__lte=0)

        return qs.order_by("title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["authors"] = Author.objects.all()
        ctx["current"] = {
            "q": self.request.GET.get("q", ""),
            "genre": self.request.GET.get("genre", ""),
            "author": self.request.GET.get("author", ""),
            "min": self.request.GET.get("min", ""),
            "max": self.request.GET.get("max", ""),
            "avail": self.request.GET.get("avail", ""),
        }
        return ctx


class BookDetailView(DetailView):
    model = Book
    context_object_name = "book"
    template_name = "catalog/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class SuggestView(View):
    def get(self, request):
        q = request.GET.get("q", "").strip()
        if not q:
            return JsonResponse({"suggestions": []})
        books = Book.objects.filter(is_active=True).prefetch_related("authors", "tags")
        results = []
        # First try simple prefix/contains
        initial = list(
            books.filter(Q(title__istartswith=q) | Q(authors__name__istartswith=q))
            .distinct()[:8]
        )
        for b in initial:
            results.append({
                "title": b.title,
                "slug": b.slug,
                "authors": ", ".join(a.name for a in b.authors.all()),
                "score": 100,
            })
        # If still under 5, extend with icontains
        if len(results) < 5:
            extra = books.filter(
                Q(title__icontains=q) | Q(authors__name__icontains=q) | Q(tags__name__icontains=q)
            ).exclude(slug__in=[r["slug"] for r in results]).distinct()[: (8 - len(results))]
            for b in extra:
                results.append({
                    "title": b.title,
                    "slug": b.slug,
                    "authors": ", ".join(a.name for a in b.authors.all()),
                    "score": 95,
                })
        # If still few and RapidFuzz available, fuzzy extend
        if len(results) < 5 and HAS_FUZZ:
            candidates = []
            for b in books:
                key = f"{b.title} {' '.join(a.name for a in b.authors.all())} {' '.join(t.name for t in b.tags.all())}"
                candidates.append((b.slug, key))
            matches = process.extract(q, dict(candidates), scorer=fuzz.WRatio, limit=8)
            for slug, score, _ in matches:
                if slug in [r["slug"] for r in results] or score < 40:
                    continue
                try:
                    b = next(b for b in books if b.slug == slug)
                    results.append({
                        "title": b.title,
                        "slug": b.slug,
                        "authors": ", ".join(a.name for a in b.authors.all()),
                        "score": score,
                    })
                except StopIteration:
                    continue
        # Final fallback: recent books
        if not results:
            for b in Book.objects.filter(is_active=True).order_by("-created_at")[:5]:
                results.append({
                    "title": b.title,
                    "slug": b.slug,
                    "authors": ", ".join(a.name for a in b.authors.all()),
                    "score": 0,
                })
        return JsonResponse({"suggestions": results})
