from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title
