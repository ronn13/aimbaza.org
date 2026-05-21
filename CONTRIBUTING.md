# Contributing to aimbaza.org

Thank you for helping build the MbazaNLP community website. This guide covers everything you need to make a contribution.

## Prerequisites

- Python 3.11+
- Git

## Local setup

```bash
git clone https://github.com/MBAZA-NLP/aimbaza.org.git
cd aimbaza.org
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements/development.txt
cp .env.example .env             # edit if needed
python manage.py migrate
python manage.py loaddata apps/events/fixtures/initial_events.json \
                             apps/blog/fixtures/initial_posts.json
python manage.py runserver
```

The site will be available at http://127.0.0.1:8000.

## Branching model

| Branch | Purpose |
|--------|---------|
| `main` | Production — deploys to aimbaza.org |
| `develop` | Staging — deploys to staging.aimbaza.org |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation-only changes |
| `content/*` | Content updates (blog posts, events, opportunities) |

**Always branch from `develop`.** Open pull requests against `develop`. `develop` is merged to `main` at release.

```bash
git checkout develop
git pull origin develop
git checkout -b feat/your-feature-name
```

## Making changes

### Code style

We use [Black](https://black.readthedocs.io) for formatting and [Flake8](https://flake8.pycqa.org) for linting.

```bash
python -m black .
python -m flake8 .
```

Both are enforced in CI. A pull request with formatting or lint errors will not be merged.

### Templates

HTML templates live in `templates/`. Follow the existing Bootstrap 5 patterns. Keep templates free of business logic — use view context for data, template tags for display logic.

### Adding content

**Blog posts** — create a `Post` object via Django admin (`/admin/`) or add an entry to `apps/blog/fixtures/`. Slug must be unique and URL-safe.

**Events** — create an `Event` object via Django admin or add to `apps/events/fixtures/`.

**Opportunities / Projects** — these pages are currently template-driven. Edit the relevant template or view context directly via a pull request.

## Running tests

```bash
python -m coverage run manage.py test apps --settings=aimbaza.settings.development
python -m coverage report --fail-under=60
```

All tests must pass and coverage must stay above 60% for a PR to merge.

## Pull request checklist

Before opening a PR:

- [ ] Branched from `develop`, not `main`
- [ ] `black .` passes with no changes
- [ ] `flake8 .` passes with no errors
- [ ] All tests pass (`manage.py test apps`)
- [ ] New views have a corresponding smoke test in `apps/core/tests.py`
- [ ] No secrets or `.env` files committed
- [ ] PR description explains **what** changed and **why**

## Commit messages

Use the imperative mood and a short subject line (≤ 72 chars):

```
feat: add opportunities filter by deadline
fix: correct Slack invite URL in footer
content: add blog post on aimbaza.org launch
docs: update local setup instructions
```

## Getting help

Open an issue on GitHub or ask in `#help` on [our Slack](https://aimbaza.slack.com).
