from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.projects.models import Project
from apps.files_management.helpers import uploaded_file_object_from_string
from .forms import UploadFileForm
from .helpers import upload_file
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from .file_conversions.tei_handler import TeiHandler
from .models import FileVersion, File
from apps.decorators import file_exist, has_access
import json


@login_required
def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files_list = request.FILES.getlist("file")

        try:
            parent_dir_id = int(request.POST.get("parent_dir"))
        except:
            parent_dir_id = None

        try:
            project = Project.objects.filter(id=request.POST.get("project")).get()
        except Project.DoesNotExist:
            return HttpResponseBadRequest("Invalid project id")

        upload_statuses = {}

        for file in files_list:
            file_name = file.name

            upload_status = {file_name: {'uploaded': False, 'migrated': False, 'message': None}}
            upload_statuses.update(upload_status)

            try:
                dbfile = upload_file(file, project, request.user, parent_dir_id)

                upload_status = {'uploaded': True}
                upload_statuses[file_name].update(upload_status)

                file_version = FileVersion.objects.get(file_id=dbfile.id, number=dbfile.version_number)
                path_to_file = file_version.upload.path

                tei_handler = TeiHandler(path_to_file)
                migration, is_tei_p5_prefixed = tei_handler.recognize()

                if migration:
                    tei_handler.migrate()

                    migrated_string = tei_handler.text.read()

                    uploaded_file = uploaded_file_object_from_string(migrated_string, file_name)

                    upload_file(uploaded_file, project, request.user, parent_dir_id)

                    migration_status = {'migrated': True, 'message': tei_handler.get_message()}
                    upload_statuses[file_name].update(migration_status)

            except Exception as exception:
                upload_status = {'message': str(exception)}
                upload_statuses[file_name].update(upload_status)

        response = json.dumps(upload_statuses)

        return HttpResponse(response, status=200, content_type='application/json')

    else:
        form = UploadFileForm()
        return render(request, 'files_management/upload.html', {'form': form})


@login_required
@file_exist
@has_access()
def file(request, file_id, version_nr):  # type: (HttpRequest, int, int) -> HttpResponse
    file = File.objects.get(id=file_id)

    content = {
        'title': file.name,
        'file': file,
        'version': version_nr,
    }

    return render(request, 'files_management/file.html', content)
