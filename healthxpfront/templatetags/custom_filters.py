from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    return value * arg


@register.filter
def sub(value, arg):
    """Subtract the argument from the value"""
    return value - arg
