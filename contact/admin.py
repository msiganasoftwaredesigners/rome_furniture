from django.contrib import admin
from .models import ContactMessage
from msigana_ecommerce.admin_site import admin_site

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'created_at')
    readonly_fields = ('full_name', 'email', 'phone', 'message', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('created_at',)

admin_site.register(ContactMessage, ContactMessageAdmin)
