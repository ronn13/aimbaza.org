import datetime
from django.test import TestCase
from apps.blog.models import Post
from apps.events.models import Event


class SmokeTests(TestCase):
    """HTTP 200 smoke tests for all public routes."""

    def setUp(self):
        Post.objects.create(
            title="Test Post",
            slug="test-post",
            excerpt="excerpt",
            body="body",
            published=datetime.date.today(),
            is_published=True,
        )
        Event.objects.create(
            title="Test Event",
            date=datetime.date.today(),
            location="Kigali",
        )

    def _ok(self, path):
        self.assertEqual(self.client.get(path).status_code, 200)

    def test_home(self):
        self._ok("/")

    def test_projects(self):
        self._ok("/projects/")

    def test_events(self):
        self._ok("/events/")

    def test_blog(self):
        self._ok("/blog/")

    def test_blog_detail(self):
        self._ok("/blog/test-post/")

    def test_opportunities(self):
        self._ok("/opportunities/")

    def test_community(self):
        self._ok("/community/")

    def test_gallery(self):
        self._ok("/gallery/")

    def test_contribute(self):
        self._ok("/contribute/")

    def test_services(self):
        self._ok("/services/")

    def test_robots_txt(self):
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Disallow: /admin/", resp.content)

    def test_sitemap(self):
        self._ok("/sitemap.xml")

    def test_demos(self):
        self._ok("/demos/")

    def test_about_redirects(self):
        resp = self.client.get("/about/")
        self.assertIn(resp.status_code, (301, 302))
        self.assertEqual(resp["Location"], "/")

    def test_community_partners(self):
        self._ok("/community/partners/")
