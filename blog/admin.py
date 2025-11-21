from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "staffer", "published_at", "is_published")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "excerpt", "body", "staffer")
    prepopulated_fields = {"slug": ("title",)}
