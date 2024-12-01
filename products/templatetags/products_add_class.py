
from django import template

register = template.Library()

@register.filter(name='add_class_products')
def add_class_products(value, css_class):
    return value.as_widget(attrs={"class": css_class})
