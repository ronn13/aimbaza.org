import pathlib
import yaml
from django.shortcuts import render

_DATA_DIR = pathlib.Path(__file__).parent / "data"

_TYPE_META = {
    "funding": ("Funding", "fas fa-hand-holding-dollar", "success"),
    "data": ("Data", "fas fa-database", "primary"),
    "research": ("Research", "fas fa-microscope", "warning"),
    "community": ("Community", "fas fa-people-group", "info"),
}

_CAL_TYPE_META = {
    "sprint": ("Sprint", "fas fa-bolt", "primary"),
    "grant": ("Grant", "fas fa-file-contract", "success"),
    "event": ("Event", "fas fa-calendar-star", "warning"),
    "workshop": ("Workshop", "fas fa-chalkboard-teacher", "secondary"),
    "call": ("Call", "fas fa-phone", "info"),
}


def _load_partners():
    with open(_DATA_DIR / "partners.yaml", encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    partners = {}
    for p in entries:
        if not p.get("active", True):
            continue
        t = p.get("type", "community")
        label, icon, colour = _TYPE_META.get(
            t, ("Partner", "fas fa-handshake", "secondary")
        )
        p["type_label"] = label
        p["type_icon"] = icon
        p["type_colour"] = colour
        partners[p["id"]] = p
    return partners


def _load_calendar(partners):
    with open(_DATA_DIR / "collaboration_calendar.yaml", encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    result = []
    for e in entries:
        if not e.get("active", True):
            continue
        t = e.get("type", "event")
        label, icon, colour = _CAL_TYPE_META.get(
            t, ("Event", "fas fa-calendar", "secondary")
        )
        e["type_label"] = label
        e["type_icon"] = icon
        e["type_colour"] = colour
        e["partners"] = [
            partners[pid] for pid in e.get("partner_ids", []) if pid in partners
        ]
        result.append(e)
    result.sort(key=lambda x: x["date"])
    return result


def index(request):
    return render(request, "community/community.html")


def partners(request):
    partner_list = list(_load_partners().values())
    cal = _load_calendar(_load_partners())
    return render(
        request,
        "community/partners.html",
        {
            "partners": partner_list,
            "calendar": cal,
        },
    )
