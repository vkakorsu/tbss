from django.urls import path
from .views import CatalogListView, BookDetailView, SuggestView

app_name = "catalog"

urlpatterns = [
    path("", CatalogListView.as_view(), name="index"),
    path("book/<slug:slug>/", BookDetailView.as_view(), name="detail"),
    path("suggest/", SuggestView.as_view(), name="suggest"),
]
