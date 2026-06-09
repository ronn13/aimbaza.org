"""
Fetches international AI/NLP events from RSS feeds and appends them to
apps/events/data/international_events.yaml.

Filters for:
  - Africa-relevant content (location or organisation keywords)
  - NLP / AI / machine learning topic keywords
  - Sponsorship / travel grant mentions (flagged as has_sponsorship: true)

Pinned entries are never modified.

Run:
    python manage.py fetch_events
    python manage.py fetch_events --dry-run
    python manage.py fetch_events --days 90   # look back further
"""

import re
import datetime
import pathlib
import textwrap

import feedparser
import yaml
from django.core.management.base import BaseCommand

DATA_FILE = pathlib.Path(__file__).parents[2] / "data" / "international_events.yaml"

# At least one Africa keyword AND one NLP/AI keyword must appear.
AFRICA_KEYWORDS = [
    "africa",
    "african",
    "rwanda",
    "kenya",
    "nigeria",
    "ghana",
    "ethiopia",
    "uganda",
    "tanzania",
    "senegal",
    "ivory coast",
    "côte d'ivoire",
    "nairobi",
    "kigali",
    "lagos",
    "addis ababa",
    "abuja",
    "accra",
    "dakar",
    "cape town",
    "johannesburg",
    "cairo",
    "kampala",
    "dar es salaam",
    "indaba",
    "masakhane",
    "africanlp",
    "ai4d",
]

NLP_AI_KEYWORDS = [
    "nlp",
    "natural language",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    " ai ",
    "language model",
    "llm",
    "computational linguistics",
    "speech recognition",
    "machine translation",
    "named entity",
    "sentiment analysis",
    "text classification",
    "neural network",
    "transformer",
    "bert",
    "low-resource",
    "multilingual",
    "kinyarwanda",
    "swahili",
    "amharic",
    "hausa",
]

SPONSORSHIP_KEYWORDS = [
    "travel grant",
    "scholarship",
    "sponsored",
    "financial support",
    "stipend",
    "bursary",
    "funded participation",
    "fellowship",
    "grant for attendance",
    "d&i",
    "diversity",
    "financial assistance",
    "registration fee waiver",
    "free registration",
    "sponsored attendance",
]

RSS_SOURCES = [
    {
        "source_id": "opportunity-desk-events",
        "rss_url": "https://opportunitydesk.org/category/events/feed/",
        "source_name": "Opportunity Desk",
    },
    {
        "source_id": "datascienceafrica",
        "rss_url": "https://www.datascienceafrica.org/feed/",
        "source_name": "Data Science Africa",
    },
    {
        "source_id": "deeplearningindaba",
        "rss_url": "https://deeplearningindaba.com/blog/feed/",
        "source_name": "Deep Learning Indaba",
    },
    {
        "source_id": "masakhane",
        "rss_url": "https://www.masakhane.io/feed.xml",
        "source_name": "Masakhane",
    },
    {
        "source_id": "ai4d-africa",
        "rss_url": "https://ai4d.ai/feed/",
        "source_name": "AI4D Africa",
    },
    {
        "source_id": "wikicfp-africa-nlp",
        "rss_url": "https://www.wikicfp.com/cfp/rss?q=Africa+NLP",
        "source_name": "WikiCFP",
    },
    {
        "source_id": "wikicfp-africa-ai",
        "rss_url": "https://www.wikicfp.com/cfp/rss?q=Africa+AI",
        "source_name": "WikiCFP",
    },
]

LOOKBACK_DAYS_DEFAULT = 60


def _slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)[:60]


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _normalise(text):
    return " " + _strip_html(text or "").lower() + " "


def _has_any(text, keywords):
    normalised = _normalise(text)
    return any(kw in normalised for kw in keywords)


def _truncate(text, length=240):
    text = " ".join(_strip_html(text).split())
    return textwrap.shorten(text, width=length, placeholder="...")


def _entry_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.date(*entry.published_parsed[:3])
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime.date(*entry.updated_parsed[:3])
    return None


class Command(BaseCommand):
    help = "Fetch international AI/NLP events from RSS feeds and update international_events.yaml"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--days",
            type=int,
            default=LOOKBACK_DAYS_DEFAULT,
            help="Only consider RSS entries published within this many days (default: 60)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        cutoff = datetime.date.today() - datetime.timedelta(days=options["days"])

        with open(DATA_FILE, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []

        existing_urls = {e["url"] for e in entries if e.get("url")}
        added = []

        for source in RSS_SOURCES:
            self.stdout.write(
                f"Fetching {source['source_name']} ({source['rss_url']}) ..."
            )
            try:
                feed = feedparser.parse(source["rss_url"])
            except Exception as exc:
                self.stderr.write(f"  Error: {exc}")
                continue

            for entry in feed.entries:
                link = entry.get("link", "")
                if not link or link in existing_urls:
                    continue

                pub_date = _entry_date(entry)
                if pub_date and pub_date < cutoff:
                    continue

                title = entry.get("title", "").strip()
                summary = entry.get("summary") or entry.get("description") or ""
                haystack = title + " " + summary

                if not _has_any(haystack, AFRICA_KEYWORDS):
                    continue
                if not _has_any(haystack, NLP_AI_KEYWORDS):
                    continue

                has_sponsorship = _has_any(haystack, SPONSORSHIP_KEYWORDS)
                sponsorship_details = ""
                if has_sponsorship:
                    # extract the first sentence that contains a sponsorship keyword
                    for sentence in re.split(r"[.!?]", _strip_html(summary)):
                        if _has_any(sentence, SPONSORSHIP_KEYWORDS):
                            sponsorship_details = sentence.strip()
                            break

                slug = f"{source['source_id']}-{_slugify(title)}"
                new_entry = {
                    "id": slug,
                    "title": title,
                    "description": _truncate(summary, 240),
                    "url": link,
                    "location": "Africa (see link for details)",
                    "date": None,
                    "deadline": None,
                    "has_sponsorship": has_sponsorship,
                    "sponsorship_details": sponsorship_details,
                    "source": source["source_name"],
                    "pinned": False,
                    "added_date": str(datetime.date.today()),
                    "active": True,
                }

                existing_urls.add(link)
                entries.append(new_entry)
                badge = " [SPONSORED]" if has_sponsorship else ""
                added.append(f"{title}{badge}")

                if dry_run:
                    self.stdout.write(f"  [dry-run] Would add: {title}{badge}")
                else:
                    self.stdout.write(f"  Added: {title}{badge}")

        if not added:
            self.stdout.write("No new events found.")
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
                    f"Done — {len(added)} new events written to {DATA_FILE}"
                )
            )
        else:
            self.stdout.write(f"[dry-run] {len(added)} events would be added.")
