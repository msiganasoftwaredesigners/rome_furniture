# models.py
from django.db import models

class HeadContent(models.Model):
    header_meta_data = models.TextField(blank=True, null=True)
    footer_meta_data = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Header: {self.header_meta_data[:50]}, Footer: {self.footer_meta_data[:50]}"