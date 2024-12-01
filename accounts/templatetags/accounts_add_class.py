
from django import template

register = template.Library()

@register.filter(name='add_class_accounts')
def add_class_accounts(value, css_class):
    return value.as_widget(attrs={"class": css_class})
