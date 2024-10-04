from django.contrib import admin
from .models import Footer
from msigana_ecommerce.admin_site import admin_site

class FooterAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # if Footer object already exists, do not allow new ones to be added
        if Footer.objects.exists():
            return False
        return super().has_add_permission(request)

admin_site.register(Footer, FooterAdmin)