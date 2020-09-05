from django import template


register = template.Library()

@register.inclusion_tag('help/bottom_hint.html')
def bottom_hint(call_to_action, content):
    return {'call_to_action': call_to_action, 'content': content}