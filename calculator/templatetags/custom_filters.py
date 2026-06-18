from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_decimal(value):
    if value is None:
        return ''
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except:
            return str(value)
    if value == value.to_integral():
        return str(int(value))
    else:
        return f"{value:.2f}".replace('.', ',')

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return value * arg
    except (TypeError, ValueError):
        return value