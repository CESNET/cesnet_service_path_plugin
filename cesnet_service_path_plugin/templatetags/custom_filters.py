from django import template

register = template.Library()


@register.filter
def spacecomma(value):
    """
    Converts a number to a string with spaces as thousand separators.
    """
    try:
        # Handle both int and float
        if isinstance(value, float) or (isinstance(value, str) and "." in value):
            value = float(value)
            return f"{value:,.2f}".replace(",", " ")
        else:
            value = int(value)
            return f"{value:,}".replace(",", " ")
    except (ValueError, TypeError):
        return value
