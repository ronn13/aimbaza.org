from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Post


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return [
            "core:home",
            "projects:index",
            "events:index",
            "blog:index",
            "opportunities:index",
            "community:index",
            "gallery:index",
            "core:contribute",
            "core:services",
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published

    def location(self, obj):
        return reverse("blog:detail", args=[obj.slug])
