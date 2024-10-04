from django.contrib import admin
from .models import Post
from msigana_ecommerce.admin_site import admin_site

from django.utils.text import slugify
from django.utils.html import strip_tags

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    def save_model(self, request, obj, form, change):
        obj.slug = slugify(strip_tags(obj.title))
        super().save_model(request, obj, form, change)

admin_site.register(Post, PostAdmin)