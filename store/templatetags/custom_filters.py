from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    if arg is None:
        return value
    return value - arg