# store/templatetags/color_filters.py
from django import template

register = template.Library()

@register.filter
def get_color(color_dict, key):
    return color_dict.get(key)