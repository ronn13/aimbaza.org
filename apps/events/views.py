import datetime
from django.shortcuts import render
from .models import Event


def index(request):
    today = datetime.date.today()
    upcoming = Event.objects.filter(date__gte=today)
    past = Event.objects.filter(date__lt=today)
    return render(request, "events/events.html", {"upcoming": upcoming, "past": past})
