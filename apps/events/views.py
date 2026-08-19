import calendar as cal_lib
import datetime
import pathlib

import yaml
from django.shortcuts import render

from .models import Event

_DATA_FILE = pathlib.Path(__file__).parent / "data" / "international_events.yaml"

MONTH_NAMES = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
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
                    row.append(
                        {
                            "day": day,
                            "date": d,
                            "events": events_by_date.get(d, []),
                            "is_today": d == today,
                        }
                    )
            annotated.append(row)

        months.append(
            {
                "name": f"{MONTH_NAMES[month]} {year}",
                "weeks": annotated,
                "day_headers": DAY_HEADERS,
            }
        )
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def _load_international():
    with open(_DATA_FILE, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    return [e for e in entries if e.get("active", True)]


def _annotate_international(events, today):
    """Parse date/deadline strings and attach display-ready values to each event."""
    for e in events:
        for field in ("date", "deadline"):
            raw = e.get(field)
            if raw:
                try:
                    e[f"_{field}_parsed"] = datetime.date.fromisoformat(str(raw))
                except ValueError:
                    e[f"_{field}_parsed"] = None
            else:
                e[f"_{field}_parsed"] = None

        d = e["_date_parsed"]
        if d:
            e["date_display"] = f"{d.day} {d.strftime('%b %Y')}"
            e["date_is_past"] = d < today
        else:
            e["date_display"] = None
            e["date_is_past"] = False

        dl = e["_deadline_parsed"]
        e["deadline_display"] = f"{dl.day} {dl.strftime('%b %Y')}" if dl else None

    return events


def _sort_by_date(events):
    """Sort events by date ascending; events with no date go last."""
    return sorted(
        events,
        key=lambda e: (
            e["_date_parsed"] is None,
            e["_date_parsed"] or datetime.date.min,
        ),
    )


def index(request):
    today = datetime.date.today()

    inhouse_upcoming = list(Event.objects.filter(date__gte=today))
    inhouse_past = list(Event.objects.filter(date__lt=today).order_by("-date")[:5])

    calendar_months = _build_calendar(today, inhouse_upcoming)

    international = _annotate_international(_load_international(), today)
    sponsored = _sort_by_date([e for e in international if e.get("has_sponsorship")])
    other = _sort_by_date([e for e in international if not e.get("has_sponsorship")])

    return render(
        request,
        "events/events.html",
        {
            "calendar_months": calendar_months,
            "inhouse_upcoming": inhouse_upcoming,
            "inhouse_past": inhouse_past,
            "sponsored_events": sponsored,
            "other_events": other,
            "today": today,
        },
    )
