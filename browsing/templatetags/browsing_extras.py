from django import template
from django.contrib.contenttypes.models import ContentType
register = template.Library()


@register.simple_tag
def nav_menu(app=None):

    """creates links to all class of the passed in application
    for which get_listview_url() methods have been registered"""

    if app:
        models = ContentType.objects.filter(app_label=app)
        result = []
        for x in models:
            modelname = x.name
            modelname = modelname.replace(" ", "").lower()
            try:
                fetched_model = ContentType.objects.get(
                    app_label=app, model=modelname).model_class()
                item = {
                    'name': modelname.title(),
                }
            except Exception as e:
                print(e)
                item = {
                    'name': None
                }
            try:
                item['link'] = fetched_model.get_listview_url()
                result.append(item)
            except AttributeError:
                item['link'] = None
        return result


@register.inclusion_tag('browsing/tags/class_definition.html', takes_context=True)
def class_definition(context):
    values = {}
    try:
        values['class_name'] = context['class_name']
        values['docstring'] = context['docstring']
    except Exception as e:
        print(e)
        pass
    return values


@register.inclusion_tag('browsing/tags/column_selector.html', takes_context=True)
def column_selector(context):
    try:
        return {'columns': context['togglable_colums']}
    except Exception as e:
        print(e)
        return {'columns': None}
