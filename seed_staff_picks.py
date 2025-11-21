import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from blog.models import Post  # noqa: E402


TITLE = "5 Books Every Ghanaian Student Should Read"

EXCERPT = (
    "From Ghanaian classics to African literature and global bestsellers, "
    "these five books challenge, inspire, and broaden the worldview of any student."
)

BODY = """
For Ghanaian students, reading isn't just about passing exams – it's about seeing
ourselves on the page, understanding the world, and sharpening how we think.

Here are five books on our shelves we believe every Ghanaian student should read:

1. **Things Fall Apart** by Chinua Achebe  
   A foundation of modern African literature. Achebe's portrait of Okonkwo and
   pre‑colonial Igbo society is essential for understanding how culture, power,
   and history collide – and how stories can reclaim African voices.

2. **Half of a Yellow Sun** by Chimamanda Ngozi Adichie  
   A powerful, human story set during the Biafran War. It challenges students to
   think critically about nationhood, conflict, and empathy – far beyond what a
   history textbook can offer.

3. **The Beautiful Ones Are Not Yet Born** by Ayi Kwei Armah  
   A Ghanaian classic that speaks directly to our context. Armah's sharp look at
   corruption and personal integrity will resonate with any student thinking
   about leadership, responsibility, and the future of Ghana.

4. **Born a Crime** by Trevor Noah  
   Hilarious and heartbreaking in equal measure. Noah's story of growing up in
   apartheid and post‑apartheid South Africa makes big themes like race,
   identity, and inequality feel immediate and real.

5. **Atomic Habits** by James Clear  
   Not African, but extremely practical. This is the book we recommend to
   students who want to build better study routines, stay consistent, and make
   small changes that add up over a term or an academic year.

These titles are available at TBSS, and our team is always happy to recommend
more based on your interests – whether you're preparing for WASSCE, university,
or simply building a personal reading life.
""".strip()


def seed():
    post, created = Post.objects.get_or_create(
        slug="5-books-every-ghanaian-student-should-read",
        defaults={
            "title": TITLE,
            "excerpt": EXCERPT,
            "body": BODY,
            "staffer": "TBSS Staff",
        },
    )
    if not created:
        # keep it up to date if you re-run
        post.title = TITLE
        post.excerpt = EXCERPT
        post.body = BODY
        post.staffer = "TBSS Staff"
        post.save(update_fields=["title", "excerpt", "body", "staffer"])
        print("Updated existing staff pick post.")
    else:
        print("Created staff pick post.")


if __name__ == "__main__":
    seed()
