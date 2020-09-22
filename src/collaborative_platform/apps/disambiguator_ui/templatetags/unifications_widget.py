from django import template


register = template.Library()

@register.inclusion_tag('disambiguator_ui/unifications_widget.html')
def unifications_widget():
    return {}
