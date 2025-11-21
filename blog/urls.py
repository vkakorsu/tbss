from django.urls import path
from .views import BlogIndexView, PostDetailView

app_name = "blog"

urlpatterns = [
    path("", BlogIndexView.as_view(), name="index"),
    path("<slug:slug>/", PostDetailView.as_view(), name="detail"),
]
