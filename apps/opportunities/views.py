import pathlib
import yaml
from django.shortcuts import render

_DATA_FILE = (
    pathlib.Path(__file__).parent / "data" / "opportunities.yaml"
)
_CATEGORY_ORDER = ["computing", "grants", "fellowships"]
_CATEGORY_LABELS = {
    "computing": ("Computing Access", "fas fa-server", "primary"),
    "grants": ("Grants &amp; Funding", "fas fa-hand-holding-dollar", "success"),
    "fellowships": ("Fellowships &amp; Residencies", "fas fa-user-graduate", "warning"),
}


def _load_opportunities():
    with open(_DATA_FILE, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    grouped = {cat: [] for cat in _CATEGORY_ORDER}
    for entry in entries:
        if not entry.get("active", True):
            continue
        cat = entry.get("category", "grants")
        if cat in grouped:
            grouped[cat].append(entry)
    return [
        {
            "key": cat,
            "label": _CATEGORY_LABELS[cat][0],
            "icon": _CATEGORY_LABELS[cat][1],
            "colour": _CATEGORY_LABELS[cat][2],
            "items": grouped[cat],
        }
        for cat in _CATEGORY_ORDER
        if grouped[cat]
    ]


def index(request):
    return render(
        request,
        "opportunities/opportunities.html",
        {"categories": _load_opportunities()},
    )
