from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def contribute(request):
    return render(request, "core/contribute.html")


def services(request):
    return render(request, "core/services.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Sitemap: https://aimbaza.org/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
