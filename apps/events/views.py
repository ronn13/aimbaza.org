import calendar as cal_lib
import datetime
import pathlib

import yaml
from django.shortcuts import render

from .models import Event

_DATA_FILE = pathlib.Path(__file__).parent / "data" / "international_events.yaml"

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _build_calendar(today, inhouse_events, n_months=3):
    """Return n_months worth of annotated calendar data for the template."""
    events_by_date = {}
    for ev in inhouse_events:
        events_by_date.setdefault(ev.date, []).append(ev)

    months = []
    year, month = today.year, today.month
    for _ in range(n_months):
        weeks = cal_lib.monthcalendar(year, month)
        annotated = []
        for week in weeks:
            row = []
            for day in week:
                if day == 0:
                    row.append({"day": None, "events": [], "is_today": False})
                else:
                    d = datetime.date(year, month, day)
                    row.append({
                        "day": day,
                        "date": d,
                        "events": events_by_date.get(d, []),
                        "is_today": d == today,
                    })
            annotated.append(row)

        months.append({
            "name": f"{MONTH_NAMES[month]} {year}",
            "weeks": annotated,
            "day_headers": DAY_HEADERS,
        })
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def _load_international():
    with open(_DATA_FILE, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    return [e for e in entries if e.get("active", True)]


def index(request):
    today = datetime.date.today()

    inhouse_upcoming = list(Event.objects.filter(date__gte=today))
    inhouse_past = list(Event.objects.filter(date__lt=today).order_by("-date")[:5])

    calendar_months = _build_calendar(today, inhouse_upcoming)

    international = sorted(
        _load_international(),
        key=lambda e: (
            not e.get("has_sponsorship", False),  # sponsored first
            e.get("added_date", ""),
        ),
        reverse=False,
    )
    # Sort: sponsored first, then by added_date descending for non-sponsored
    sponsored = [e for e in international if e.get("has_sponsorship")]
    other = [e for e in international if not e.get("has_sponsorship")]

    return render(request, "events/events.html", {
        "calendar_months": calendar_months,
        "inhouse_upcoming": inhouse_upcoming,
        "inhouse_past": inhouse_past,
        "sponsored_events": sponsored,
        "other_events": other,
        "today": today,
    })
