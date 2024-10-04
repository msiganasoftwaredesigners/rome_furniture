from django.contrib.admin import AdminSite as DjangoAdminSite
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.urls import resolve
from django.http import Http404


class AdminSite(DjangoAdminSite):
    site_header ='Rome Furniture Login'
    site_title = 'Rome Furniture Admin'

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Get the resolved app_label from the request URL
        resolved_url = resolve(request.path_info)
        app_label = resolved_url.kwargs.get('app_label')

        if app_label:
            # If app_label is present in the URL, filter app_list accordingly
            app_list = [app_dict.get(app_label)]
        else:
            # If no app_label present, show all apps
            app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        # Move the 'store' app to the top.
        store_app = next((app for app in app_list if app['app_label'] == 'contact'), None)
        if store_app:
            app_list.remove(store_app)
            app_list.insert(0, store_app)

        # Move the 'contact' app next to the 'store' app.
        orders_app = next((app for app in app_list if app['app_label'] == 'store'), None)
        if orders_app:
            app_list.remove(orders_app)
            app_list.insert(1, orders_app)

        orders_app = next((app for app in app_list if app['app_label'] == 'blog'), None)
        if orders_app:
            app_list.remove(orders_app)
            app_list.insert(2, orders_app)
        
        orders_app = next((app for app in app_list if app['app_label'] == 'footer'), None)
        if orders_app:
            app_list.remove(orders_app)
            app_list.insert(3, orders_app)
        return app_list
    
    def app_index(self, request, app_label, extra_context=None):
        app_list = self.get_app_list(request)

        if not app_list:
            raise Http404("The requested admin page does not exist.")

        context = {
            **self.each_context(request),
            "title": _("%(app)s administration") % {"app": app_list[0]["name"]},
            "subtitle": None,
            "app_list": app_list,
            "app_label": app_label,
        **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(
            request,
            self.app_index_template
            or ["admin/%s/app_index.html" % app_label, "admin/app_index.html"],
            context,
        )



admin_site = AdminSite(name='admin')