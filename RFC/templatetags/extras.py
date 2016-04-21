from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()
# template cannot access names starting with '_'
@register.filter
def get_id(op):
    return op._id


@register.filter
def get_string(obj):
    return obj.__str__()


@register.filter
def get_state(obj):
    d = dict(obj.STATE_CHOICE)
    return d[obj.cur_state].replace('_', ' ')

@register.filter
def get_direction(obj):
    d = dict(obj.DIR_CHOICE)
    return d[obj.direction].replace('_', ' ')

@register.filter
def is_direction_forward(obj):
    return obj.direction % 2

@register.filter
def is_direction_backward(obj):
    return obj.direction // 2

@register.filter
def is_manager(user):
    try:
        group = user.groups.get(name="managers")
        return True
    except ObjectDoesNotExist:
        return False

@register.filter
def is_tech(user):
    try:
        group = user.groups.get(name="tech team")
        return True
    except ObjectDoesNotExist:
        return False
