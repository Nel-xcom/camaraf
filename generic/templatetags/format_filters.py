from django import template

register = template.Library()

@register.filter
def formato_pesos(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    parts = f"{value:,.2f}".split(".")
    integer_part = parts[0].replace(",", ".")  # miles con puntos
    decimal_part = parts[1]
    return f"{integer_part},{decimal_part}"
