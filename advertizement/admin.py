from django.contrib import admin
from .models import Favicon
from msigana_ecommerce.admin_site import admin_site


    
class FaviconAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if Favicon.objects.exists():
            return False
        return super().has_add_permission(request)
    

admin_site.register(Favicon, FaviconAdmin)