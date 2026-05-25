from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title

    @property
    def is_multi_day(self):
        return self.end_date and self.end_date != self.date
