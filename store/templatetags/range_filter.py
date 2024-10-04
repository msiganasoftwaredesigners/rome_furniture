# your_app/templatetags/range_filter.py

from django import template

register = template.Library()

@register.filter
def to_range(value):
    if value is None:
        return []
    return range(round(value))