from django import template


register = template.Library()

@register.inclusion_tag('help/no_projects_hint.html')
def no_projects_hint():
    return {}