from django import template

register = template.Library()

@register.filter
def discounted_price(price):
    try:
        price = float(price)
        return price - (price * 0.15)
    except ValueError:
        return price