from django.core.cache import cache
from .models import  Favicon



def favicon(request):
    favicon = cache.get('favicon')
    if not favicon:
        favicon = Favicon.objects.first()
        cache.set('favicon', favicon, 60*60*00)  
    return {'favicon': favicon}