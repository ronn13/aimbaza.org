from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("projects/", include("apps.projects.urls")),
    path("events/", include("apps.events.urls")),
    path("blog/", include("apps.blog.urls")),
    path("opportunities/", include("apps.opportunities.urls")),
    path("community/", include("apps.community.urls")),
    path("gallery/", include("apps.gallery.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
