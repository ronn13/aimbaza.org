# aimbaza.org

Django site for the MBAZA-NLP open-source language AI community.

## Development

```bash
cp .env.example .env
pip install -r requirements/development.txt
python manage.py runserver
```

## Deployment

- **Production:** Namecheap cPanel — auto-deploys from `main` via GitHub Actions SSH
- **Staging:** Render free tier — auto-deploys from `develop` via `render.yaml`

See `WP1-W1_Architecture_Decision.md` in the parent repo for full architecture notes.
