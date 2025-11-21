from django.urls import path
from .views import ReviewsIndexView, add_review

app_name = "reviews"

urlpatterns = [
    path("", ReviewsIndexView.as_view(), name="index"),
    path("add/<slug:slug>/", add_review, name="add"),
]
