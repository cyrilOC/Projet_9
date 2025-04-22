from django import template

register = template.Library()

@register.filter(name='class_name')
def class_name(value):
    """
    Retourne le nom de classe d'un objet
    Usage: {{ object|class_name }}
    """
    return value.__class__.__name__