import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from lxml.etree import XMLSyntaxError

from apps.files_management.file_conversions.ids_filler import IDsFiller
from apps.files_management.helpers import uploaded_file_object_from_string, extract_text_and_entities, index_entities
from apps.projects.models import Project
from apps.views_decorators import objects_exists, user_has_access

from .file_conversions.tei_handler import TeiHandler
from .forms import UploadFileForm
from .helpers import upload_file
from .models import FileVersion, File


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
                migration, is_tei_p5_unprefixed = tei_handler.recognize()

                if not migration and not is_tei_p5_unprefixed:
                    upload_status = {"message": "Invalid filetype, please provide TEI file or compatible ones.",
                                     "uploaded": False}
                    upload_statuses[file_name].update(upload_status)
                    dbfile.delete()
                    continue

                if migration:
                    tei_handler.migrate()

                try:
                    tei_handler = IDsFiller(tei_handler, file_name)
                except XMLSyntaxError:
                    is_id_filled = False
                else:
                    is_id_filled = tei_handler.process()

                if migration or is_id_filled:
                    migrated_string = tei_handler.text.read()

                    text, entities = extract_text_and_entities(migrated_string, project.id, dbfile.id)
                    index_entities(entities)

                    uploaded_file = uploaded_file_object_from_string(migrated_string, file_name)

                    upload_file(uploaded_file, project, request.user, parent_dir_id)

                    migration_status = {'migrated': True, 'message': tei_handler.get_message()}
                    upload_statuses[file_name].update(migration_status)
                else:
                    file.seek(0)
                    text, entities = extract_text_and_entities(file.read(), project.id, dbfile.id)
                    index_entities(entities)

            except ValueError as exception:
                upload_status = {'message': str(exception)}
                upload_statuses[file_name].update(upload_status)

        response = json.dumps(upload_statuses)

        return HttpResponse(response, status=200, content_type='application/json')

    else:
        form = UploadFileForm()
        return render(request, 'files_management/upload.html', {'form': form})


@login_required
@objects_exists
@user_has_access()
def file(request, file_id, version=None):  # type: (HttpRequest, int, int) -> HttpResponse

    file = File.objects.get(id=file_id)

    if version is None:
        version = file.version_number

    content = {
        'title': file.name,
        'file': file,
        'version': version,
    }

    return render(request, 'files_management/file.html', content)
