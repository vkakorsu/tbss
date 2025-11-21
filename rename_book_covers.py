"""One-off utility to rename existing book covers to title-based filenames.

Usage (from project root, venv activated):

    python rename_book_covers.py

Make sure you've run migrations so Book.cover uses book_cover_upload.
"""

import os
from pathlib import Path

import django
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from catalog.models import Book, book_cover_upload  # noqa: E402


def main():
    base_dir = Path(__file__).resolve().parent
    print("Base dir:", base_dir)

    renamed = 0
    skipped = 0

    for book in Book.objects.exclude(cover=""):
        old_field = book.cover
        old_name = old_field.name  # e.g. "covers/oldname.jpg"
        if not old_name:
            skipped += 1
            continue

        # Desired new relative path based on current title
        new_name = book_cover_upload(book, os.path.basename(old_name))
        if new_name == old_name:
            skipped += 1
            continue

        storage = old_field.storage

        if not storage.exists(old_name):
            print(f"Missing file for {book.id} ({book.title}): {old_name}")
            skipped += 1
            continue

        # Read contents and save under new name
        with storage.open(old_name, "rb") as f:
            content = f.read()

        # Save to new path
        book.cover.save(new_name, ContentFile(content), save=False)

        # Optionally delete old file if different path
        if old_name != new_name and storage.exists(old_name):
            storage.delete(old_name)

        book.save(update_fields=["cover"])
        renamed += 1
        print(f"Renamed: {old_name} -> {new_name}")

    print(f"Done. Renamed: {renamed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
