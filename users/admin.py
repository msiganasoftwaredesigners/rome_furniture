from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from msigana_ecommerce.admin_site import admin_site
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.utils.html import escape
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import Group



class StaffUser(CustomUser):
    class Meta:
        proxy = True

class CustomerUser(CustomUser):
    class Meta:
        proxy = True

class NoAddUserAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class StaffUserAdmin(NoAddUserAdmin):  # Use admin.ModelAdmin instead of UserAdmin
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = StaffUser
    change_password_form = AdminPasswordChangeForm
    list_display = ("email", "first_name","username", "last_name", "is_active","is_ordersuperuser")
    list_filter = ("is_staff", "is_active",)
    readonly_fields = ("point_reward","username", "referral_code", 'is_active', 'email')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # editing an existing object
            if not request.user.is_superuser and request.user != obj:
                readonly_fields.extend(['username','first_name','last_name','facebook_url', 'telegram_url', 'whatsapp_url'])  # make 'username' read-only
        return readonly_fields
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "username")}),
        ("Permissions", {"fields": ("is_staff", "is_active","is_ordersuperuser", "groups", "user_permissions")}),
        ("Social Links", {"fields": ("facebook_url", "telegram_url", "whatsapp_url")}),
    )
    add_fieldsets = (
        (None, {
             "classes": ("wide",),
             "fields": (
                 "email", "password1", "password2", "is_staff",
                 "is_active", "groups", "user_permissions", "first_name", "last_name"
             )}
        ),
        ("Social Links", {
            "fields": ("facebook_url", "telegram_url", "whatsapp_url")}
        ),
   )
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.fieldsets
        return (
            (None, {"fields": ("email", "password")}),
            ("Personal Info", {"fields": ("first_name", "last_name", "username")}),
            ("Social Links", {"fields": ("facebook_url", "telegram_url", "whatsapp_url")}),
        )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('<id>/password/', self.admin_site.admin_view(self.user_change_password), name='auth_user_password_change'),
        ]
        return my_urls + urls
    
    def user_change_password(self, request, id, form_url=''):
        if not request.user.is_superuser:
            # Redirect to a different page or show an error message
            return HttpResponseRedirect('..')
        print(request.POST)
        user = CustomerUser.objects.get(pk=id)
        if 'password1' in request.POST and 'password2' in request.POST:
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                return HttpResponseRedirect('..')
            else:
                print(form.errors)
        else:
            form = self.change_password_form(user)
        fieldsets = [(None, {'fields': form.base_fields})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})
        context = {
            'title': 'Change password: %s' % escape(user),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': '_popup' in request.POST,
            'add': False,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request, [
            "admin/auth/user/change_password.html"
        ], context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def password_change_link(self, obj):
        if obj.pk:  # if object has already been saved and has a primary key, show password change link
            url = reverse('admin:auth_user_password_change', args=[obj.pk])
            return format_html('<a href="{}">Change password</a>', url)
        return ""

    password_change_link.short_description = 'Password change link'  # sets column name
    list_display = ("email", "first_name", "last_name", "is_active", "password_change_link",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].disabled = not is_superuser

        if 'is_ordersuperuser' in form.base_fields:
            form.base_fields['is_ordersuperuser'].disabled = not is_superuser
        return form

    def get_queryset(self, request):
        return self.model.objects.filter(is_staff=True)


class CustomerUserAdmin(NoAddUserAdmin):  # Use admin.ModelAdmin instead of UserAdmin
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomerUser
    change_password_form = AdminPasswordChangeForm
    list_filter = ("is_staff", "is_active",)
    readonly_fields = ('is_active','username', 'email' )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        else:
            return self.readonly_fields + ('point_reward', 'referral_code', 'is_active')
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "username","last_name", "point_reward","referral_code")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2",
                "is_active", "groups", "user_permissions", "first_name", "last_name"
            )}
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('<id>/password/', self.admin_site.admin_view(self.user_change_password), name='auth_user_password_change'),
        ]
        return my_urls + urls
    
    def user_change_password(self, request, id, form_url=''):
        print(request.POST)
        user = CustomerUser.objects.get(pk=id)
        if 'password1' in request.POST and 'password2' in request.POST:
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                return HttpResponseRedirect('..')
            else:
                print(form.errors)
        else:
            form = self.change_password_form(user)
        fieldsets = [(None, {'fields': form.base_fields})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})
        context = {
            'title': 'Change password: %s' % escape(user),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': '_popup' in request.POST,
            'add': False,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request, [
            "admin/auth/user/change_password.html"
        ], context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def password_change_link(self, obj):
        if obj.pk:  # if object has already been saved and has a primary key, show password change link
            url = reverse('admin:auth_user_password_change', args=[obj.pk])
            return format_html('<a href="{}">Change password</a>', url)
        return ""

    password_change_link.short_description = 'Password change link'  # sets column name
    list_display = ("email", "username", "phone_number", "first_name", "last_name", "is_active", "password_change_link",)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        form.base_fields['is_staff'].disabled = not is_superuser
        return form
    
    def get_queryset(self, request):
        return self.model.objects.filter(is_staff=False)
    
admin_site.register(StaffUser, StaffUserAdmin) 
admin_site.register(CustomerUser, CustomerUserAdmin)  
admin_site.register(Group)
admin_site.register(SocialApp)
admin_site.register(SocialAccount)
admin_site.register(SocialToken)