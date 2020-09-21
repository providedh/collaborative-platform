from django import template


register = template.Library()

@register.inclusion_tag('help/project_overlay.html', takes_context=True)
def project_overlay(context):
    return context
