#!/usr/bin/env python3
"""Slack news bot for MbazaNLP.

Posts two digest types to the #general channel via an incoming webhook:
  - weekly      Upcoming events + open opportunities
  - fortnightly GitHub org releases/repos + HuggingFace model/dataset updates

Usage:
    python scripts/slack_news_bot.py weekly
    python scripts/slack_news_bot.py fortnightly

Required env vars:
    SLACK_WEBHOOK_URL   Slack incoming webhook URL
    GH_TOKEN            GitHub PAT (fortnightly only)
    HF_TOKEN            HuggingFace token (fortnightly only, optional)
"""

import json
import os
import pathlib
import sys
from datetime import date, timedelta

import requests
import yaml

REPO_ROOT = pathlib.Path(__file__).parent.parent
WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
GH_TOKEN = os.environ.get("GH_TOKEN", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

SITE_URL = "https://aimbaza.org"
GH_ORG = "MBAZA-NLP"
HF_ORG = "mbazaNLP"

CAT_ICONS = {
    "computing": ":computer:",
    "grants": ":money_with_wings:",
    "fellowships": ":mortar_board:",
}


# ── helpers ───────────────────────────────────────────────────────────────────


def post_to_slack(blocks):
    resp = requests.post(WEBHOOK_URL, json={"blocks": blocks}, timeout=10)
    resp.raise_for_status()


def load_yaml(rel_path):
    with open(REPO_ROOT / rel_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_json(rel_path):
    with open(REPO_ROOT / rel_path, encoding="utf-8") as f:
        return json.load(f)


def link(url, text):
    return f"<{url}|{text}>" if url else text


# ── weekly digest ─────────────────────────────────────────────────────────────


def _upcoming_community_events(window_days=30):
    today = date.today()
    cutoff = today + timedelta(days=window_days)
    items = load_json("apps/events/fixtures/initial_events.json")
    upcoming = []
    for item in items:
        f = item["fields"]
        event_date = date.fromisoformat(f["date"])
        if today <= event_date <= cutoff:
            upcoming.append(f)
    return sorted(upcoming, key=lambda e: e["date"])


def _deadline_events(window_days=30):
    today = date.today()
    cutoff = today + timedelta(days=window_days)
    events = load_yaml("apps/events/data/international_events.yaml")
    results = []
    for e in events:
        if not e.get("active", True):
            continue
        dl = e.get("deadline")
        if dl and today <= date.fromisoformat(str(dl)) <= cutoff:
            results.append(e)
    return results


def _active_opportunities(limit=6):
    opps = load_yaml("apps/opportunities/data/opportunities.yaml")
    return [o for o in opps if o.get("active", True)][:limit]


def weekly_blocks():
    today = date.today()
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":calendar: MbazaNLP Weekly Digest — {today.strftime('%d %b %Y')}",  # noqa: E501
            },
        },
        {"type": "divider"},
    ]

    # Community events in the next 30 days
    events = _upcoming_community_events()
    if events:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Upcoming Community Events*"},
            }
        )
        for e in events:
            start = date.fromisoformat(e["date"]).strftime("%d %b %Y")
            end = e.get("end_date")
            date_str = (
                f"{start} – {date.fromisoformat(end).strftime('%d %b')}"
                if end and end != e["date"]
                else start
            )
            title = link(e.get("url", ""), e["title"])
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {title} — _{e['location']}_ · {date_str}",
                    },
                }
            )
        blocks.append({"type": "divider"})

    # International events with approaching deadlines
    deadline_events = _deadline_events()
    if deadline_events:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Deadlines Approaching*"},
            }
        )
        for e in deadline_events:
            dl_str = date.fromisoformat(str(e["deadline"])).strftime("%d %b %Y")
            title = link(e.get("url", ""), e["title"])
            funding = (
                " :moneybag: _funding available_" if e.get("has_sponsorship") else ""
            )
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {title} — deadline {dl_str}{funding}",
                    },
                }
            )
        blocks.append({"type": "divider"})

    # Open opportunities
    opps = _active_opportunities()
    if opps:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Open Opportunities*"},
            }
        )
        for o in opps:
            icon = CAT_ICONS.get(o.get("category", "grants"), ":bulb:")
            title = link(o.get("url", ""), o["title"])
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"{icon} {title}"},
                }
            )
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Full list → <{SITE_URL}/opportunities/|aimbaza.org/opportunities/>",  # noqa: E501
                },
            }
        )
        blocks.append({"type": "divider"})

    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"<{SITE_URL}|aimbaza.org> · "
                        f"<{SITE_URL}/events/|Events> · "
                        f"<{SITE_URL}/opportunities/|Opportunities>"
                    ),
                }
            ],
        }
    )
    return blocks


# ── fortnightly digest ────────────────────────────────────────────────────────


def _gh_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    return headers


def _recent_github_activity(window_days=14):
    cutoff = (date.today() - timedelta(days=window_days)).isoformat()
    resp = requests.get(
        f"https://api.github.com/orgs/{GH_ORG}/events",
        headers=_gh_headers(),
        params={"per_page": 100},
        timeout=15,
    )
    resp.raise_for_status()

    releases, new_repos, seen_repos = [], [], set()
    for ev in resp.json():
        if (ev.get("created_at") or "")[:10] < cutoff:
            break
        etype = ev.get("type")
        if etype == "ReleaseEvent" and ev["payload"].get("action") == "published":
            rel = ev["payload"]["release"]
            releases.append(
                {
                    "repo": ev["repo"]["name"].split("/")[-1],
                    "name": rel.get("name") or rel.get("tag_name", ""),
                    "url": rel.get("html_url", ""),
                }
            )
        elif etype == "CreateEvent" and ev["payload"].get("ref_type") == "repository":
            repo_name = ev["repo"]["name"].split("/")[-1]
            if repo_name not in seen_repos:
                new_repos.append(
                    {
                        "name": repo_name,
                        "url": f"https://github.com/{GH_ORG}/{repo_name}",
                    }
                )
                seen_repos.add(repo_name)
    return releases, new_repos


def _recent_hf_activity(window_days=14):
    cutoff = (date.today() - timedelta(days=window_days)).isoformat()
    hf_headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

    def fetch(endpoint):
        resp = requests.get(
            f"https://huggingface.co/api/{endpoint}",
            params={"author": HF_ORG, "sort": "lastModified", "limit": 10},
            headers=hf_headers,
            timeout=15,
        )
        if not resp.ok:
            return []
        results = []
        for item in resp.json():
            last_mod = (item.get("lastModified") or item.get("last_modified") or "")[
                :10
            ]
            if last_mod >= cutoff:
                results.append(item["id"])
        return results

    return fetch("models"), fetch("datasets")


def fortnightly_blocks():
    today = date.today()
    releases, new_repos = _recent_github_activity()
    hf_models, hf_datasets = _recent_hf_activity()

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f":satellite: MbazaNLP Changelog — {today.strftime('%d %b %Y')}",  # noqa: E501
            },
        },
        {"type": "divider"},
    ]

    has_content = False

    if releases:
        has_content = True
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": "*New Releases*"}}
        )
        for r in releases[:5]:
            title = link(r["url"], r["name"])
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":package: `{r['repo']}` — {title}",
                    },
                }
            )
        blocks.append({"type": "divider"})

    if new_repos:
        has_content = True
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*New Repositories*"},
            }
        )
        for r in new_repos[:5]:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":file_folder: {link(r['url'], r['name'])}",
                    },
                }
            )
        blocks.append({"type": "divider"})

    if hf_models:
        has_content = True
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Updated Models on HuggingFace*"},
            }
        )
        for model_id in hf_models[:5]:
            name = model_id.split("/")[-1]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":brain: {link(f'https://huggingface.co/{model_id}', name)}",  # noqa: E501
                    },
                }
            )
        blocks.append({"type": "divider"})

    if hf_datasets:
        has_content = True
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Updated Datasets on HuggingFace*"},
            }
        )
        for ds_id in hf_datasets[:5]:
            name = ds_id.split("/")[-1]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":card_box: {link(f'https://huggingface.co/datasets/{ds_id}', name)}",  # noqa: E501
                    },
                }
            )
        blocks.append({"type": "divider"})

    if not has_content:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_No new releases or activity in the last 14 days._",
                },
            }
        )

    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"<https://github.com/{GH_ORG}|github.com/{GH_ORG}> · "
                        f"<https://huggingface.co/{HF_ORG}|hf.co/{HF_ORG}> · "
                        f"<{SITE_URL}|aimbaza.org>"
                    ),
                }
            ],
        }
    )
    return blocks


# ── entry point ───────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("weekly", "fortnightly"):
        print(f"Usage: {sys.argv[0]} weekly|fortnightly", file=sys.stderr)
        sys.exit(1)

    digest_type = sys.argv[1]
    blocks = weekly_blocks() if digest_type == "weekly" else fortnightly_blocks()
    post_to_slack(blocks)
    print(f"Posted {digest_type} digest to Slack.")


if __name__ == "__main__":
    main()
