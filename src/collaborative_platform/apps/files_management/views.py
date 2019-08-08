from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.projects.models import Project
from .forms import UploadFileForm
from .files_management import upload_file
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest


@login_required()
def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        try:
            parent_dir_id = int(request.POST.get("parent_dir"))
        except:
            parent_dir_id = None

        try:
            project = Project.objects.filter(id=request.POST.get("project")).get()
        except Project.DoesNotExist:
            return HttpResponseBadRequest("Invalid project id")

        upload_file(request.FILES['file'], project, request.user, parent_dir_id)
        return HttpResponse('OK')
    else:
        form = UploadFileForm()
        return render(request, 'files_management/upload.html', {'form': form})
