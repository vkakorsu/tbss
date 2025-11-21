from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View


class SubscribeView(View):
    def post(self, request):
        return HttpResponseRedirect(reverse("home"))

    def get(self, request):
        return HttpResponseRedirect(reverse("home"))
