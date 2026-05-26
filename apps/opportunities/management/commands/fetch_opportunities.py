"""
Fetches new opportunities from configured RSS feeds and appends them to
apps/opportunities/data/opportunities.yaml.

Pinned entries are never modified. New entries from RSS are added only if:
  - their URL is not already in the YAML, and
  - their title or summary contains at least one opportunity keyword.

Run:
    python manage.py fetch_opportunities
    python manage.py fetch_opportunities --dry-run
"""

import re
import datetime
import pathlib
import textwrap

import feedparser
import yaml
from django.core.management.base import BaseCommand

DATA_FILE = pathlib.Path(__file__).parents[4] / "data" / "opportunities.yaml"

OPPORTUNITY_KEYWORDS = [
    "grant",
    "fellowship",
    "apply",
    "call for",
    "funding",
    "open call",
    "award",
    "scholarship",
    "deadline",
    "opportunity",
    "residency",
]

# RSS sources to monitor. pinned entries in the YAML with the same id are
# never touched; these sources only produce new auto-added entries.
RSS_SOURCES = [
    {
        "source_id": "lacuna-fund",
        "rss_url": "https://lacunafund.org/feed/",
        "category": "grants",
        "source_name": "Lacuna Fund",
    },
    {
        "source_id": "mozilla-foundation",
        "rss_url": "https://foundation.mozilla.org/en/feed/",
        "category": "grants",
        "source_name": "Mozilla Foundation",
    },
    {
        "source_id": "ai4d-africa",
        "rss_url": "https://ai4d.ai/feed/",
        "category": "grants",
        "source_name": "AI4D Africa",
    },
    {
        "source_id": "masakhane",
        "rss_url": "https://www.masakhane.io/feed.xml",
        "category": "fellowships",
        "source_name": "Masakhane",
    },
    {
        "source_id": "opportunity-desk",
        "rss_url": "https://opportunitydesk.org/feed/",
        "category": "fellowships",
        "source_name": "Opportunity Desk",
    },
]


def _slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)[:60]


def _is_opportunity(entry):
    haystack = ((entry.get("title") or "") + " " + (entry.get("summary") or "")).lower()
    return any(kw in haystack for kw in OPPORTUNITY_KEYWORDS)


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _truncate(text, length=200):
    text = _strip_html(text)
    text = " ".join(text.split())
    return textwrap.shorten(text, width=length, placeholder="...")


class Command(BaseCommand):
    help = "Fetch new opportunities from RSS feeds and update opportunities.yaml"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be added without writing to disk",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        with open(DATA_FILE, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []

        existing_urls = {e["url"] for e in entries if e.get("url")}
        added = []

        for source in RSS_SOURCES:
            self.stdout.write(f"Fetching {source['source_name']} ...")
            try:
                feed = feedparser.parse(source["rss_url"])
            except Exception as exc:
                self.stderr.write(f"  Error fetching {source['rss_url']}: {exc}")
                continue

            for entry in feed.entries:
                link = entry.get("link", "")
                if not link or link in existing_urls:
                    continue
                if not _is_opportunity(entry):
                    continue

                title = entry.get("title", "").strip()
                description = _truncate(
                    entry.get("summary") or entry.get("description") or "", 200
                )
                slug = f"{source['source_id']}-{_slugify(title)}"

                new_entry = {
                    "id": slug,
                    "title": f"{source['source_name']}: {title}",
                    "category": source["category"],
                    "description": description,
                    "url": link,
                    "button_text": "Read more →",
                    "pinned": False,
                    "added_date": str(datetime.date.today()),
                    "active": True,
                }

                existing_urls.add(link)
                entries.append(new_entry)
                added.append(new_entry["title"])

                if dry_run:
                    self.stdout.write(f"  [dry-run] Would add: {new_entry['title']}")
                else:
                    self.stdout.write(f"  Added: {new_entry['title']}")

        if not added:
            self.stdout.write("No new opportunities found.")
            return

        if not dry_run:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                yaml.dump(
                    entries,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done — {len(added)} new entries written to {DATA_FILE}"
                )
            )
        else:
            self.stdout.write(f"[dry-run] {len(added)} entries would be added.")
