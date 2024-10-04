from django.contrib import admin
from .models import HeadContent
from msigana_ecommerce.admin_site import admin_site

class HeadContentAdmin(admin.ModelAdmin):
    list_display = ('header_meta_data','footer_meta_data')

    def has_add_permission(self, request):
        # if HeadContent object already exists, do not allow new ones to be added
        if HeadContent.objects.exists():
            return False
        return super().has_add_permission(request)

admin_site.register(HeadContent, HeadContentAdmin)