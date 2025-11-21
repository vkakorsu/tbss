import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from catalog.models import Author, Publisher, Genre, Book  # noqa: E402

BOOKS = [
    {
        "title": "Things Fall Apart",
        "authors": ["Chinua Achebe"],
        "publisher": "Heinemann",
        "genres": ["Fiction", "African Literature"],
        "isbn": "9780000000001",
        "price": Decimal("85.00"),
        "stock": 20,
        "featured": True,
    },
    {
        "title": "Half of a Yellow Sun",
        "authors": ["Chimamanda Ngozi Adichie"],
        "publisher": "Fourth Estate",
        "genres": ["Fiction", "Historical"],
        "isbn": "9780000000002",
        "price": Decimal("95.00"),
        "stock": 15,
        "featured": True,
    },
    {
        "title": "The Alchemist",
        "authors": ["Paulo Coelho"],
        "publisher": "HarperCollins",
        "genres": ["Fiction", "Philosophy"],
        "isbn": "9780000000003",
        "price": Decimal("70.00"),
        "stock": 25,
        "featured": False,
    },
    {
        "title": "Atomic Habits",
        "authors": ["James Clear"],
        "publisher": "Penguin",
        "genres": ["Self-Help", "Productivity"],
        "isbn": "9780000000004",
        "price": Decimal("120.00"),
        "stock": 18,
        "featured": True,
    },
    {
        "title": "Becoming",
        "authors": ["Michelle Obama"],
        "publisher": "Crown",
        "genres": ["Memoir"],
        "isbn": "9780000000005",
        "price": Decimal("110.00"),
        "stock": 12,
        "featured": False,
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "authors": ["Yuval Noah Harari"],
        "publisher": "Harper",
        "genres": ["Non-fiction", "History"],
        "isbn": "9780000000006",
        "price": Decimal("130.00"),
        "stock": 10,
        "featured": False,
    },
    {
        "title": "Born a Crime",
        "authors": ["Trevor Noah"],
        "publisher": "Spiegel & Grau",
        "genres": ["Memoir", "Humor"],
        "isbn": "9780000000007",
        "price": Decimal("90.00"),
        "stock": 14,
        "featured": False,
    },
    {
        "title": "The Hobbit",
        "authors": ["J. R. R. Tolkien"],
        "publisher": "Allen & Unwin",
        "genres": ["Fantasy"],
        "isbn": "9780000000008",
        "price": Decimal("80.00"),
        "stock": 16,
        "featured": False,
    },
    {
        "title": "A Promised Land",
        "authors": ["Barack Obama"],
        "publisher": "Crown",
        "genres": ["Memoir", "Politics"],
        "isbn": "9780000000009",
        "price": Decimal("125.00"),
        "stock": 9,
        "featured": False,
    },
    {
        "title": "The Beautiful Ones Are Not Yet Born",
        "authors": ["Ayi Kwei Armah"],
        "publisher": "Heinemann",
        "genres": ["Fiction", "African Literature"],
        "isbn": "9780000000010",
        "price": Decimal("75.00"),
        "stock": 22,
        "featured": True,
    },
]


def get_or_create_authors(names):
    objs = []
    for name in names:
        obj, _ = Author.objects.get_or_create(name=name)
        objs.append(obj)
    return objs


def get_or_create_publisher(name):
    obj, _ = Publisher.objects.get_or_create(name=name)
    return obj


def get_or_create_genres(names):
    objs = []
    for name in names:
        obj, _ = Genre.objects.get_or_create(name=name)
        objs.append(obj)
    return objs


def seed():
    created, updated = 0, 0
    for item in BOOKS:
        authors = get_or_create_authors(item["authors"])
        publisher = get_or_create_publisher(item["publisher"])
        genres = get_or_create_genres(item["genres"])

        book, is_created = Book.objects.get_or_create(
            isbn=item["isbn"],
            defaults={
                "title": item["title"],
                "publisher": publisher,
                "price": item["price"],
                "stock": item["stock"],
                "is_active": True,
                "is_featured": item["featured"],
            },
        )
        if not is_created:
            # Update some fields if it exists
            book.title = item["title"]
            book.publisher = publisher
            book.price = item["price"]
            book.stock = item["stock"]
            book.is_featured = item["featured"]
            book.is_active = True
            book.save()
            updated += 1
        else:
            created += 1

        # M2M relations
        book.authors.set(authors)
        book.genres.set(genres)
        book.save()

    print(f"Seed complete. Created: {created}, Updated: {updated}")


if __name__ == "__main__":
    seed()
