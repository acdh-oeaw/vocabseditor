from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django_celery_results.models import TaskResult

from vocabs.forms import UploadFileForm
from vocabs.tasks import export_concept_schema, import_concept_schema
from vocabs.utils import handle_uploaded_file


def export_async(request):
    get_format = request.GET.get('format', default='pretty-xml')
    schema_id = request.GET.get('schema-id')
    export_concept_schema.delay(schema_id, get_format)
    return redirect('vocabs:job-status')


@login_required
def import_async(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_format = file.name.split('.')[-1]
            if file_format in ['ttl', 'rdf']:
                file_format = file.name.split('.')[-1]
                full_path = handle_uploaded_file(file)
                import_concept_schema.delay(
                    full_path,
                    request.user.username,
                    file_format=file_format,
                    language=form.cleaned_data['language']
                )
                messages.info(request, f"Started Import of {file.name}")
            else:
                messages.error(request, "Upload rdf or ttl file")
            return redirect('vocabs:job-status')
    else:
        form = UploadFileForm()
    return render(request, 'vocabs/upload.html', {'form': form})


class TaskResultListView(ListView):
    model = TaskResult
    paginate_by = 100
    template_name = "vocabs/taskresult_list.j2"
