from django.shortcuts import redirect
from django.views.generic.list import ListView
from django_celery_results.models import TaskResult

from vocabs.tasks import export_concept_schema


def export_async(request):
    get_format = request.GET.get('format', default='pretty-xml')
    schema_id = request.GET.get('schema-id')
    export_concept_schema.delay(schema_id, get_format)
    return redirect('vocabs:export-status')


class TaskResultListView(ListView):
    model = TaskResult
    paginate_by = 100
    template_name = "vocabs/taskresult_list.j2"
