# context_processors.py
from .models import HeadContent

def head_contents(request):
    return {'head_contents': HeadContent.objects.all()}