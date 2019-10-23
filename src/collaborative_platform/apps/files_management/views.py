from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.views_decorators import objects_exists, user_has_access
from .models import File


@login_required
@objects_exists
@user_has_access()
def file(request, file_id, version=None):  # type: (HttpRequest, int, int) -> HttpResponse

    file = File.objects.get(id=file_id, deleted=False)

    if version is None:
        version = file.version_number

    content = {
        'title': file.name,
        'file': file,
        'version': version,
    }

    return render(request, 'files_management/file.html', content)


@login_required
@objects_exists
@user_has_access()
def fileversions(request, file_id):  # type: (HttpRequest, int) -> HttpResponse

    file = File.objects.get(id=file_id, deleted=False)

    content = {
        'title': file.name,
        'file': file,
        'versions': file.version_number
    }

    return render(request, 'files_management/fileversions.html', content)
