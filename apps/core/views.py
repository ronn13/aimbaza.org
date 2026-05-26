import datetime

from django.http import HttpResponse
from django.shortcuts import render

from apps.events.models import Event


def home(request):
    today = datetime.date.today()
    upcoming = list(Event.objects.filter(date__gte=today).order_by("date")[:3])
    return render(request, "core/home.html", {"upcoming_events": upcoming})


def contribute(request):
    return render(request, "core/contribute.html")


def services(request):
    return render(request, "core/services.html")


def demos(request):
    return render(request, "core/demos.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Sitemap: https://aimbaza.org/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
