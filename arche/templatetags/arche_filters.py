from django import template
register = template.Library()


@register.filter(name="truncate_inverse")
def truncate_inverse(value, max_length=25):
    if len(value) > max_length:
        truncd_val = value[-max_length:]
        return "...{}".format(truncd_val)
    else:
        return value
