from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "published", "is_published"]
    list_filter = ["is_published", "published"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "body"]
    date_hierarchy = "published"
