import os
from django.shortcuts import render
from django.conf import settings


def index(request):
    photo_dir = os.path.join(
        settings.STATICFILES_DIRS[0], "gallery", "bakame_april_2023"
    )
    thumbs_dir = os.path.join(photo_dir, "thumbs")
    try:
        filenames = sorted(
            f for f in os.listdir(photo_dir) if f.lower().endswith(".jpg")
        )
    except FileNotFoundError:
        filenames = []
    photos = [
        {
            "url": f"gallery/bakame_april_2023/{f}",
            "thumb_url": (
                f"gallery/bakame_april_2023/thumbs/{f}"
                if os.path.exists(os.path.join(thumbs_dir, f))
                else f"gallery/bakame_april_2023/{f}"
            ),
            "alt": "Bakame community event, April 2023",
        }
        for f in filenames
    ]
    return render(request, "gallery/gallery.html", {"photos": photos})
