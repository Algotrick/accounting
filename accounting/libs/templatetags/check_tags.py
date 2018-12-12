from django import template

register = template.Library()


@register.inclusion_tag('_generics/check_tag.html')
def render_check(check):
    return {
        'check': check,
    }
