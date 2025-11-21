from django.urls import path
from .views import PaymentsIndexView, momo_start

app_name = "payments"

urlpatterns = [
    path("", PaymentsIndexView.as_view(), name="index"),
    path("momo/start/<str:order_number>/", momo_start, name="momo_start"),
]
