from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Publisher, Genre, Tag, Book
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
import csv
from io import TextIOWrapper


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "price", "stock", "is_active", "cover_preview")
    list_filter = ("is_active", "genres", "publisher")
    search_fields = ("title", "isbn", "authors__name")
    filter_horizontal = ("authors", "genres", "tags")
    prepopulated_fields = {"slug": ("title",)}
    actions = ["increase_stock_5", "decrease_stock_5"]

    def cover_preview(self, obj):
        if obj.cover:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;"/>', obj.cover.url)
        return ""
    cover_preview.short_description = "Cover"

    class CsvImportForm(forms.Form):
        csv_file = forms.FileField()

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("upload-csv/", self.admin_site.admin_view(self.upload_csv), name="catalog_book_upload_csv"),
        ]
        return custom + urls

    def upload_csv(self, request):
        context = {"title": "Bulk import books via CSV"}
        if request.method == "POST":
            form = self.CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                f = TextIOWrapper(request.FILES["csv_file"].file, encoding="utf-8")
                reader = csv.DictReader(f)
                created = 0
                for row in reader:
                    title = row.get("title", "").strip()
                    if not title:
                        continue
                    isbn = row.get("isbn", "").strip()
                    price = row.get("price", "0").strip() or "0"
                    stock = int(row.get("stock", "0") or 0)
                    desc = row.get("description", "")
                    pub_name = row.get("publisher", "").strip()
                    author_names = [a.strip() for a in row.get("authors", row.get("author", "")).split(";") if a.strip()]
                    genre_names = [g.strip() for g in row.get("genres", "").split(";") if g.strip()]
                    tag_names = [t.strip() for t in row.get("tags", "").split(";") if t.strip()]

                    publisher = None
                    if pub_name:
                        publisher, _ = Publisher.objects.get_or_create(name=pub_name)

                    book, created_flag = Book.objects.get_or_create(isbn=isbn or None, defaults={
                        "title": title,
                        "description": desc,
                        "price": price,
                        "stock": stock,
                        "publisher": publisher,
                        "is_active": True,
                    })
                    if not created_flag:
                        book.title = title or book.title
                        book.description = desc or book.description
                        book.price = price or book.price
                        book.stock = stock
                        if publisher:
                            book.publisher = publisher
                        book.save()
                    # M2M
                    for name in author_names:
                        a, _ = Author.objects.get_or_create(name=name)
                        book.authors.add(a)
                    for name in genre_names:
                        g, _ = Genre.objects.get_or_create(name=name)
                        book.genres.add(g)
                    for name in tag_names:
                        t, _ = Tag.objects.get_or_create(name=name)
                        book.tags.add(t)
                    created += 1 if created_flag else 0
                self.message_user(request, f"CSV processed. Created {created} new books.")
                return redirect("..")
        else:
            form = self.CsvImportForm()
        context["form"] = form
        return render(request, "admin/catalog/book_upload.html", context)

    def increase_stock_5(self, request, queryset):
        for b in queryset:
            b.stock = (b.stock or 0) + 5
            b.save(update_fields=["stock"])
        self.message_user(request, "Increased stock by 5 for selected books.")

    def decrease_stock_5(self, request, queryset):
        for b in queryset:
            b.stock = max(0, (b.stock or 0) - 5)
            b.save(update_fields=["stock"])
        self.message_user(request, "Decreased stock by 5 for selected books.")
    increase_stock_5.short_description = "Increase stock by 5"
    decrease_stock_5.short_description = "Decrease stock by 5"
