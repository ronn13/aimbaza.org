from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Use plain static storage in dev/tests — no manifest required.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
