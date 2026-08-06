import os
import urllib.parse

from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
)

# Render auto-injects this; trust it so the onrender.com preview URL works.
_render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_hostname:
    ALLOWED_HOSTS.append(_render_hostname)

# Railway healthchecks originate from this fixed hostname; without it
# Django returns 400 DisallowedHost and the deploy never goes healthy.
# https://docs.railway.com/deployments/healthchecks#healthcheck-hostname
ALLOWED_HOSTS.append("healthcheck.railway.app")

# Database from DATABASE_URL env var
# Supports: postgres://USER:PASSWORD@HOST:PORT/NAME
_db_url = config("DATABASE_URL")
_parsed = urllib.parse.urlparse(_db_url)

_engine_map = {
    "postgres": "django.db.backends.postgresql",
    "postgresql": "django.db.backends.postgresql",
    "sqlite": "django.db.backends.sqlite3",
}

DATABASES = {
    "default": {
        "ENGINE": _engine_map.get(_parsed.scheme, "django.db.backends.postgresql"),
        "NAME": _parsed.path.lstrip("/"),
        "USER": _parsed.username or "",
        "PASSWORD": _parsed.password or "",
        "HOST": _parsed.hostname or "",
        "PORT": str(_parsed.port) if _parsed.port else "",
    }
}

# Security
# Trust Render's (and cPanel's) reverse proxy for HTTPS detection so
# SECURE_SSL_REDIRECT doesn't loop on platforms that terminate SSL upstream.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# Platform healthchecks (Railway, Render) hit the container directly over
# plain HTTP at "/", bypassing the edge proxy that sets X-Forwarded-Proto.
# Without this, SECURE_SSL_REDIRECT turns that into a 301 and the
# healthcheck never sees a 200.
SECURE_REDIRECT_EXEMPT = [r"^$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Canonical site URL — used by sitemap and Open Graph tags
SITE_URL = config("SITE_URL", default="https://aimbaza.org")

# Plausible analytics domain (e.g. "aimbaza.org"). Leave blank to disable.
PLAUSIBLE_DOMAIN = config("PLAUSIBLE_DOMAIN", default="")
