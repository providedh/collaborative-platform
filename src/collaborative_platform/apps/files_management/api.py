from json import dumps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse

from apps.views_decorators import file_exist, file_version_exist, has_access
from apps.files_management.models import File, FileVersion
from apps.projects.models import Contributor, Project
from .helpers import upload_file, extract_text_and_entities, index_entities
from apps.projects.models import Project
from .file_conversions.tei_handler import TeiHandler
from .helpers import upload_file,  uploaded_file_object_from_string


@login_required
def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("files")
        if not files_list:
            return HttpResponseBadRequest("File not attached properly")
        try:
            project = int(request.POST.get("project"))
            project = Project.objects.filter(id=project).get()
        except (ValueError, Project.DoesNotExist):  # TODO check level of contribution to authorize user to upload files
            return HttpResponseBadRequest("Invalid project id")
        try:
            parent_dir = int(request.POST.get("parent_dir"))
        except ValueError:
            parent_dir = None

        upload_statuses = {}

        for file in files_list:
            file_name = file.name

            upload_status = {file_name: {'uploaded': False, 'migrated': False, 'message': None}}
            upload_statuses.update(upload_status)

            try:
                dbfile = upload_file(file, project, request.user, parent_dir)

                file.seek(0)
                text, entities = extract_text_and_entities(file.read(), project.id, dbfile.id)

                index_entities(entities)

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

                    upload_file(uploaded_file, project, request.user, parent_dir)

                    migration_status = {'migrated': True, 'message': tei_handler.get_message()}
                    upload_statuses[file_name].update(migration_status)

            except Exception as exception:
                upload_status = {'message': str(exception)}
                upload_statuses[file_name].update(upload_status)

        response = dumps(upload_statuses)

        return HttpResponse(response, status=200, content_type='application/json')

    return HttpResponseBadRequest("Invalid request method or files not attached")


@login_required
@file_exist
@has_access()
def get_file_versions(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.filter(id=file_id).get()

        return JsonResponse(list(file.versions.all().values()), safe=False)

    else:
        return HttpResponseBadRequest("Invalid request method")


@login_required
@file_exist
@file_version_exist
@has_access()
def get_file_version(request, file_id, version):
    if request.method == 'GET':
        file = File.objects.filter(id=file_id).get()
        fv = file.versions.filter(number=version).get()  # type: FileVersion

        try:
            creator = model_to_dict(fv.created_by, fields=('id', 'first_name', 'last_name'))
        except (AttributeError, User.DoesNotExist):
            creator = fv.created_by_id

        fv.upload.open('r')
        response = {
            "filename": file.name,
            "version_number": fv.number,
            "creator": creator,
            "data": fv.upload.read()
        }
        fv.upload.close()

        return JsonResponse(response)

    else:
        return HttpResponseBadRequest("Invalid request method")
