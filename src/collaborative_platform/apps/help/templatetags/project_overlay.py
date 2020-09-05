from django import template


register = template.Library()

@register.inclusion_tag('help/project_overlay.html')
def project_overlay():
    return {}