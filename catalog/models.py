from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_delete
from django.dispatch import receiver


def book_cover_upload(instance, filename):
    base, ext = (filename.rsplit(".", 1) + [""])[:2]
    title_slug = slugify(instance.title or "book")
    if ext:
        return f"covers/{title_slug}.{ext.lower()}"
    return f"covers/{title_slug}"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Author(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Publisher(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Genre(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "genres"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    authors = models.ManyToManyField(Author, related_name="books")
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)
    tags = models.ManyToManyField(Tag, related_name="books", blank=True)

    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover = models.ImageField(upload_to=book_cover_upload, blank=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    page_count = models.PositiveIntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["isbn"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            self.slug = base
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:detail", kwargs={"slug": self.slug})


@receiver(post_delete, sender=Book)
def delete_book_cover_file(sender, instance, **kwargs):
    """Delete the cover file from storage when a Book is deleted."""
    if instance.cover:
        instance.cover.delete(save=False)
