from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", RedirectView.as_view(url="/", permanent=False), name="about"),
    path("contribute/", views.contribute, name="contribute"),
    path("services/", views.services, name="services"),
    path("demos/", views.demos, name="demos"),
]
