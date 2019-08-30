from json import dumps, loads
from os.path import basename
from zipfile import ZipFile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseServerError
from lxml.etree import XMLSyntaxError

from apps.files_management.file_conversions.ids_filler import IDsFiller
from apps.projects.helpers import log_activity
from apps.files_management.models import File, FileVersion, Directory
from apps.projects.models import Project
from apps.views_decorators import objects_exists, user_has_access
from .file_conversions.tei_handler import TeiHandler
from .helpers import extract_text_and_entities, index_entities, upload_file, uploaded_file_object_from_string, \
    get_directory_content


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

                    upload_file(uploaded_file, project, request.user, parent_dir)

                    migration_status = {'migrated': True, 'message': tei_handler.get_message()}
                    upload_statuses[file_name].update(migration_status)
                else:
                    file.seek(0)
                    text, entities = extract_text_and_entities(file.read(), project.id, dbfile.id)
                    index_entities(entities)

            except Exception as exception:
                upload_status = {'message': str(exception)}
                upload_statuses[file_name].update(upload_status)

        response = dumps(upload_statuses)

        return HttpResponse(response, status=200, content_type='application/json')

    return HttpResponseBadRequest("Invalid request method or files not attached")


@login_required
@objects_exists
@user_has_access()
def get_file_versions(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.filter(id=file_id).get()

        return JsonResponse(list(file.versions.all().values()), safe=False)

    else:
        return HttpResponseBadRequest("Invalid request method")


@login_required
@objects_exists
@user_has_access()
def get_file_version(request, file_id, version=None):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.filter(id=file_id).get()

        if version is None:
            version = file.version_number

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


@login_required
@objects_exists
@user_has_access('RW')
def move(request, move_to):  # type: (HttpRequest, int) -> HttpResponse
    data = request.POST.get("data")
    data = loads(data)

    for directory_id in data['directories']:
        dir = Directory.objects.filter(id=directory_id).get()
        dir.move_to(move_to)
        log_activity(project=dir.project, user=request.user, related_dir=dir, action_text="moved to")
    for file_id in data['files']:
        file = File.objects.filter(id=file_id).get()
        file.move_to(move_to)
        log_activity(project=file.project, user=request.user, file=file, action_text="moved to")

    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access('RW')
def create_directory(request, directory_id, name):  # type: (HttpRequest, int, str) -> HttpResponse
    dir = Directory.objects.filter(id=directory_id).get()  # type: Directory
    dir.create_subdirectory(name, request.user)
    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access('RW')
def delete(request, **kwargs):
    if request.method != 'DELETE':
        return HttpResponseBadRequest("Only delete method is allowed here")
    if 'directory_id' in kwargs:
        dir = Directory.objects.filter(id=kwargs['directory_id']).get()
        log_activity(project=dir.project, user=request.user, related_dir=dir, action_text="deleted")
        dir.delete()
    else:
        file = File.objects.filter(id=kwargs['file_id']).get()
        log_activity(project=file.project, user=request.user, file=file, action_text="deleted")
        file.delete()
    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access('RW')
def rename(request, **kwargs):
    if 'directory_id' in kwargs:
        file = Directory.objects.filter(id=kwargs['directory_id']).get()
    else:
        file = File.objects.filter(id=kwargs['file_id']).get()
    file.rename(kwargs['new_name'], request.user)
    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access()
def get_project_tree(request, project_id):
    try:
        base_dir = Directory.objects.filter(project_id=project_id, parent_dir=None).get()
    except Directory.DoesNotExist:
        return HttpResponseServerError(dumps({'message': "Invalid data in database"}))

    result = [get_directory_content(base_dir, 0)]

    return JsonResponse(result, safe=False)


@login_required
@objects_exists
@user_has_access()
def download_file(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    file = File.objects.filter(id=file_id).get()
    return file.download()


@login_required
@objects_exists
@user_has_access()
def download_fileversion(request, file_id, version):  # type: (HttpRequest, int, int) -> HttpResponse
    fileversion = FileVersion.objects.filter(file_id=file_id, number=version).get()
    return fileversion.download()


@login_required
@objects_exists
@user_has_access()
def download_directory(request, directory_id):  # type: (HttpRequest, int) -> HttpResponse
    dir = Directory.objects.filter(id=directory_id).get()
    files = dir.files.all()

    zf = ZipFile("/tmp/" + dir.name + ".zip", 'w')

    for file in files:
        last_version = file.versions.filter(number=file.version_number).get()
        path = last_version.upload.path
        zf.write(path, file.name)

    zf.close()

    with open(zf.filename, "rb") as F:
        content = F.read()

    response = HttpResponse(content, content_type="application/zip")
    response['Content-Disposition'] = bytes('attachment; filename="{}.zip"'.format(dir.name), 'utf-8')
    return response
