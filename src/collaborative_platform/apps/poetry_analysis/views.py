from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.files_management.models import File
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def poetry_analysis(request, project_id, file_id):
    file = File.objects.get(project_id=project_id, id=file_id, deleted=False)
    project = file.project

    context = {
        'project_id': project.id,
        'file_id': file.id,
        'file_version': file.version_number,
        'title': file.name,
        'alerts': None,
    }

    return render(request, 'poetry_analysis/poetry_analysis.html', context)
