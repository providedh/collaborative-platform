from django.shortcuts import render
from .forms import UploadFileForm
from .files_management import upload_file
from django.http import HttpRequest, HttpResponse


def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        try:
            parent_dir_id = int(request.POST.get("parent_dir"))
        except:
            parent_dir_id = None

        upload_file(request.FILES['file'], request.POST.get("project"), parent_dir_id)
        return HttpResponse('OK')
    else:
        form = UploadFileForm()
        return render(request, 'files_management/upload.html', {'form': form})
