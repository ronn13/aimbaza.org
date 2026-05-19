from django.test import TestCase


class SmokeTests(TestCase):
    """HTTP 200 smoke tests for all public routes."""

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

    def test_opportunities(self):
        self._ok("/opportunities/")

    def test_community(self):
        self._ok("/community/")

    def test_gallery(self):
        self._ok("/gallery/")
