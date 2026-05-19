import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ["DJANGO_SETTINGS_MODULE"] = "aimbaza.settings.production"

from aimbaza.wsgi import application  # noqa: E402, F401
