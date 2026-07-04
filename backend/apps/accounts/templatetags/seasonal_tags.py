from django import template
from apps.accounts.seasonal_views import get_seasonal_theme as get_theme

register = template.Library()

@register.simple_tag(name='get_seasonal_theme')
def seasonal_theme_tag():
    return get_theme()
