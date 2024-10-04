from django.contrib import admin
from category.models import Category
from msigana_ecommerce.admin_site import admin_site
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'category_slug': ('category_name',)}
    list_display = ('category_name', 'category_slug')

    def has_delete_permission(self, request, obj=None):
        return False


admin_site.register(Category, CategoryAdmin)