from django.contrib import admin
from store.models import Product, Color, Size, ProductImage, SizeVariation
from django.core.cache import cache
import nested_admin
from django.forms.models import BaseInlineFormSet
from django import forms
from msigana_ecommerce.admin_site import admin_site


class SizeVariationInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.cleaned_data and form.cleaned_data['price'] < 1:
                raise forms.ValidationError("Price should be greater than or equal to 1.")
class SizeVariationInline(nested_admin.NestedTabularInline):
    model = SizeVariation
    formset = SizeVariationInlineFormSet
    fields = ('size', 'price', 'color')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "color":
            kwargs["initial"] = [Color.objects.get_or_create(name='White')[0]]
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1 if obj is None else 0
        return extra


class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    fields = ('image', 'is_main')
    
    def get_extra(self, request, obj=None, **kwargs):
        extra = 2 if obj is None else 0
        return extra
    

class ProductAdmin(nested_admin.NestedModelAdmin):
    prepopulated_fields = {'product_slug': ('product_name',)}
    list_display = (
        'product_name','likes_count','product_phone', 'product_stock', 'category',
        'product_created_date', 'product_modified_date', 'product_is_available',
        'display_sizes'  # Custom methods for display
    )
    inlines = [SizeVariationInline, ProductImageInline]
    readonly_fields = ['product_owner']

    class Media:
        js = ('js/admin.js',)

    def display_colors(self, obj):
        return ", ".join([color.name for size_var in obj.sizevariation_set.all() for color in size_var.color.all() if color and color.name])
    def display_sizes(self, obj):
        return ", ".join([size_var.size.name for size_var in obj.sizevariation_set.all() if size_var.size])
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes Count'

    def save_model(self, request, obj, form, change):
        if not change:  # the object is being created, so set the user
            obj.product_owner = request.user
        obj.save()

    def delete_model(self, request, obj):
        # Clear the most liked products cache
        cache.delete('most_liked_products')

        # Call the original delete method
        super().delete_model(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(product_owner=request.user)
        return qs
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # remove the email field from the form if the user is not a superuser
        if not request.user.is_superuser:
            form.base_fields.pop('product_owner', None)
        return form
    
        # cache image during creation and update to handle error fields occured during form submission
    def add_view(self, request, form_url='', extra_context=None):
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super().change_view(request, object_id, form_url, extra_context)

    def render_change_form(self, request, context, *args, **kwargs):
        return super().render_change_form(request, context, *args, **kwargs)
    
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', )

    def has_delete_permission(self, request, obj=None):
        return False
    
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', )

    def has_delete_permission(self, request, obj=None):
        return False
    
admin_site.register(Product, ProductAdmin)
admin_site.register(Color, ColorAdmin)
admin_site.register(Size, SizeAdmin)

