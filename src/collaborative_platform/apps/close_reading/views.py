from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.files_management.models import File
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def close_reading(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    file = File.objects.get(project_id=project_id, id=file_id, deleted=False)

    context = {
        'title': file.name,
        'alerts': None,
        'file': file,
        'project_id': project_id,
        'file_id': file_id,
    }

    return render(request, 'close_reading/close_reading.html', context)
