from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    excerpt = models.TextField(max_length=500)
    body = models.TextField()
    author = models.CharField(max_length=100, default="MbazaNLP Community")
    published = models.DateField()
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
