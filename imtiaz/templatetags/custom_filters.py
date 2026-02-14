from django import template

register = template.Library()

@register.filter
def sum_attribute(queryset, attr):
    """
    Sums the values of a specified attribute in a queryset.
    Example: {{ cart_data|sum_attribute:"total_price" }}
    """
    return sum(getattr(obj, attr, 0) for obj in queryset)
