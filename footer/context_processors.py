from django.core.cache import cache
from .models import Footer

def footer(request):
    footer = cache.get('footer')
    if not footer:
        footer = Footer.objects.first()
        cache.set('footer', footer, 60*00)  
    return {'footer': footer}