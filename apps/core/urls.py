from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contribute/", views.contribute, name="contribute"),
    path("services/", views.services, name="services"),
    path("demos/", views.demos, name="demos"),
]
