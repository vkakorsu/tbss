from django.views.generic import ListView, DetailView
from .models import Post


class BlogIndexView(ListView):
    template_name = "blog/index.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(is_published=True).order_by("-published_at")


class PostDetailView(DetailView):
    model = Post
    context_object_name = "post"
    template_name = "blog/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
