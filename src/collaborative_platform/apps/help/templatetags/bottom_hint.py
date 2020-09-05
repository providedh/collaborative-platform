from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.tag('bottom_hint')
def bottom_hint(parser, token, *args, **kwargs):
    try:
        tagName, call_to_action = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single (quoted) argument" % token.contents.split()[0])

    nodelist = parser.parse(('end_bottom_hint',))
    parser.delete_first_token()
    return HintNode(nodelist, call_to_action[1:-1])

class HintNode(template.Node):
    def __init__(self, nodelist, call_to_action):
        self.nodelist = nodelist
        self.call_to_action = call_to_action
        
    def render(self, context):
        content = mark_safe(self.nodelist.render(context))
        hint_ctx = {
            'call_to_action': self.call_to_action,
            'content': content
        }
        return template.loader.render_to_string('help/bottom_hint.html', hint_ctx)
