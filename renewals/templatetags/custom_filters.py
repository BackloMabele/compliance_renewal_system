import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def regex_highlight(text, query):
    """
    Highlights the searched text in a string by wrapping it with <span class='highlight'>.
    """
    if not query:
        return text

    highlighted = re.sub(f'({re.escape(query)})', r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)
    return mark_safe(highlighted)
