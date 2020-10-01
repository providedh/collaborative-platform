from json import dumps, loads
from os import mkdir
from zipfile import ZipFile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse

from apps.api_vis.models import Certainty, EntityVersion, EntityProperty
from apps.exceptions import BadRequest
from apps.files_management.file_conversions.ids_corrector import IDsCorrector
from apps.files_management.file_conversions.elements_extractor import ElementsExtractor
from apps.files_management.file_conversions.tei_handler import TeiHandler
from apps.files_management.helpers import clean_name, create_uploaded_file_object_from_string, \
    delete_directory_with_contents_fake, get_directory_content, include_user, overwrite_file, upload_file
from apps.files_management.models import Directory, File, FileVersion
from apps.files_management.loggers import FilesManagementLogger
from apps.projects.helpers import log_activity, paginate_start_length, page_to_json_response
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access("RW")
def upload(request, directory_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == "POST":
        try:
            files_list = __get_files_list(request)
            directory = Directory.objects.get(id=directory_id, deleted=False)
            user = request.user

            upload_statuses = []

            for file in files_list:
                upload_status = __process_file(file, directory, user)
                upload_statuses.append(upload_status)

            response = dumps(upload_statuses)

            return HttpResponse(response, status=200, content_type='application/json')

        except BadRequest as exception:
            return HttpResponseBadRequest(str(exception))


def __get_files_list(request):
    if not request.FILES:
        raise BadRequest("File not attached")

    files_list = request.FILES.getlist("file")

    if not files_list:
        raise BadRequest("File not attached properly")

    return files_list


def __process_file(file, directory, user):
    old_file_name = file.name
    file.name = clean_name(file.name)
    file_object = None
    upload_status = {'file_name': file.name, 'uploaded': False, 'migrated': False, 'message': None}

    try:
        file_object = upload_file(file, directory.project, user, directory.id)
        upload_status.update({'uploaded': True})

        FilesManagementLogger().log_uploading_file(file_object.project.id, user.id, old_file_name, file_object.id)

        xml_content, content_updated, message = __update_file_content(file_object)

        if content_updated:
            old_file_id = file_object.id
            file_object = __update_file_object(xml_content, file_object, user)

            clone_db_objects(file_object)

            upload_status.update({'migrated': True, 'message': message})

            log_activity(directory.project, user, f"File migrated: {message} ", file_object)

            FilesManagementLogger().log_migrating_file(old_file_id, file_object.id, message)

        return upload_status

    except (BadRequest, FileExistsError) as exception:
        if file_object:
            __remove_file(file_object)
        upload_status.update({'uploaded': False, 'migrated': False, 'message': str(exception)})

        FilesManagementLogger().log_uploading_file_error(old_file_name, str(exception))

        return upload_status


def __update_file_content(file_object):
    content_binary = __get_raw_content_binary(file_object)

    tei_handler = TeiHandler()
    xml_content, migration, migration_message = tei_handler.migrate_to_tei_p5(content_binary)

    # TODO: Extract formatting xml from TeiHandler and put it here

    # TODO: Create class to remove not connected xml elements (eg. annotator without certainties, certainties without
    # TODO: existing target, certainties without any category used in project, entities without properties)

    ids_corrector = IDsCorrector()
    xml_content, correction, correction_message = ids_corrector.correct_ids(xml_content, file_object.id)

    elements_extractor = ElementsExtractor()
    xml_content, extraction, extraction_message = elements_extractor.move_elements_to_db(xml_content, file_object.id)

    # TODO: Add indexing entities in Elasticsearch

    if migration or correction or extraction:
        content_updated = True
    else:
        content_updated = False

    message = ' '.join([migration_message, correction_message, extraction_message])
    message = message.strip()

    return xml_content, content_updated, message


def __get_raw_content_binary(file_object):
    file_version = FileVersion.objects.get(file_id=file_object.id, number=file_object.version_number)
    content_binary = file_version.get_raw_content_binary()

    return content_binary


def __remove_file(file_object):
    file_object.activities.get().delete()
    file_object.delete()


def __update_file_object(xml_content, old_file, user):
    new_file = create_uploaded_file_object_from_string(xml_content, old_file.name)

    file = File.objects.get(name=new_file.name, parent_dir=old_file.parent_dir, project=old_file.project, deleted=False)
    updated_file = overwrite_file(file, new_file, user)

    return updated_file


def clone_db_objects(file):
    file_versions = file.file_versions.order_by('-number')

    last_file_version = file_versions[0]
    previous_file_version = file_versions[1]

    __clone_entities_versions(last_file_version, previous_file_version)
    __clone_certainties(last_file_version, previous_file_version)


def __clone_entities_versions(last_file_version, previous_file_version):
    entities_versions = EntityVersion.objects.filter(
        file_version=previous_file_version,
        entity__deleted_in_file_version__isnull=True
    ).order_by('id')

    for entity_version in entities_versions:
        entity_properties = EntityProperty.objects.filter(
            entity_version=entity_version,
            deleted_in_file_version__isnull=True
        ).order_by('id')

        entity_version.id = None
        entity_version.file_version = last_file_version
        entity_version.save()

        for entity_property in entity_properties:
            entity_property.id = None
            entity_property.entity_version = entity_version

        EntityProperty.objects.bulk_create(entity_properties)


def __clone_certainties(last_file_version, previous_file_version):
    certainties = Certainty.objects.filter(
        file_version=previous_file_version,
        deleted_in_file_version__isnull=True
    ).order_by('id')

    for certainty in certainties:
        certainty_categories = certainty.categories.all()

        certainty.id = None
        certainty.file_version = last_file_version
        certainty.save()

        for certainty_category in certainty_categories:
            certainty.categories.add(certainty_category)


@login_required
@objects_exists
@user_has_access()
def get_file_versions(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)

        page = paginate_start_length(request, file.file_versions.all())
        return include_user(page_to_json_response(page))

    else:
        return HttpResponseBadRequest("Invalid request method")


@login_required
@objects_exists
@user_has_access()
def file(request, *args, **kwargs):
    if request.method == "DELETE":
        return delete(request, *args, **kwargs)
    elif request.method == "GET":
        return file_version(request, *args, **kwargs)


@login_required
@objects_exists
@user_has_access()
def file_version(request, file_id, version=None):  # type: (HttpRequest, int, int) -> HttpResponse
    file = File.objects.get(id=file_id, deleted=False)

    if version is None:
        version = file.version_number

    file_version = file.file_versions.get(number=version)

    try:
        creator = model_to_dict(file_version.created_by, fields=('id', 'first_name', 'last_name'))
    except (AttributeError, User.DoesNotExist):
        creator = file_version.created_by_id

    xml_content = file_version.get_rendered_content()

    response = {
        "filename": file.name,
        "version_number": file_version.number,
        "creator": creator,
        "data": xml_content
    }

    return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def move(request, move_to):  # type: (HttpRequest, int) -> HttpResponse
    data = request.body
    data = loads(data)

    move_to_dir = Directory.objects.get(id=move_to, deleted=False)

    statuses = []

    for directory_id in data.get('directories', ()):
        dir = Directory.objects.get(id=directory_id, deleted=False)

        try:
            dir.move_to(move_to)
        except (ReferenceError, IntegrityError) as e:
            statuses.append(str(e))
        else:
            log_activity(project=dir.project, user=request.user, related_dir=dir,
                         action_text="moved {} to {}".format(dir.name, move_to_dir.name))
            statuses.append("OK")

    for file_id in data.get('files', ()):
        file = File.objects.get(id=file_id, deleted=False)

        try:
            file.move_to(move_to)
        except (ReferenceError, IntegrityError) as e:
            statuses.append(str(e))
        else:
            log_activity(project=file.project, user=request.user, file=file,
                         action_text="moved file to {}: ".format(move_to_dir.name))
            statuses.append('OK')

    return JsonResponse(statuses, safe=False)


@login_required
@objects_exists
@user_has_access('RW')
def create_directory(request, directory_id, name):  # type: (HttpRequest, int, str) -> HttpResponse
    name = clean_name(name)

    dir = Directory.objects.get(id=directory_id, deleted=False)  # type: Directory
    dir.create_subdirectory(name, request.user)
    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access('RW')
def delete(request, **kwargs):
    if request.method != 'DELETE':
        return HttpResponseBadRequest("Only delete method is allowed here")

    if 'directory_id' in kwargs:
        # TODO: create `Directory` object method from `delete_directory_with_contents_fake()` function

        delete_directory_with_contents_fake(kwargs['directory_id'], request.user)

    elif 'file_id' in kwargs:
        file = File.objects.get(id=kwargs['file_id'], deleted=False)
        log_activity(project=file.project, user=request.user, action_text=f"deleted file {file.name}")
        file.delete_fake(request.user)

        FilesManagementLogger().log_deleting_file(file.project.id, request.user.id, file.id)

    else:
        return HttpResponseBadRequest("Invalid arguments")

    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access('RW')
def rename(request, **kwargs):
    if 'directory_id' in kwargs:
        file = Directory.objects.get(id=kwargs['directory_id'], deleted=False)
    else:
        file = File.objects.get(id=kwargs['file_id'], deleted=False)

    new_name = clean_name(kwargs['new_name'])

    file.rename(new_name, request.user)
    return HttpResponse("OK")


@login_required
@objects_exists
@user_has_access()
def get_project_tree(request, project_id):
    try:
        base_dir = Directory.objects.get(project_id=project_id, parent_dir=None, deleted=False)
    except Directory.DoesNotExist:
        return HttpResponseServerError(dumps({'message': "Invalid data in database"}))

    result = [get_directory_content(base_dir, 0)]

    return JsonResponse(result, safe=False)


@login_required
@objects_exists
@user_has_access()
def download_file(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    file = File.objects.get(id=file_id, deleted=False)
    content = file.get_rendered_content()

    response = HttpResponse(content, content_type='application/xml')
    response['Content-Disposition'] = bytes(f'attachment; filename="{file.name}"', 'utf-8')

    return response


@login_required
@objects_exists
@user_has_access()
def download_file_version(request, file_id, version):  # type: (HttpRequest, int, int) -> HttpResponse
    file_version = FileVersion.objects.get(file_id=file_id, number=version)
    content = file_version.get_rendered_content()

    response = HttpResponse(content, content_type='application/xml')
    response['Content-Disposition'] = bytes(f'attachment; filename="{file_version.file.name}"', 'utf-8')

    return response


@login_required
@objects_exists
@user_has_access()
def download_directory(request, directory_id):  # type: (HttpRequest, int) -> HttpResponse
    mkdir("/tmp/dummy")
    dir = Directory.objects.get(id=directory_id, deleted=False)
    zf = ZipFile("/tmp/" + dir.name + ".zip", 'w')

    def pack_dir(dir):
        zf.write("/tmp/dummy", dir.get_path())
        for file in dir.files.all():
            last_version = file.file_versions.get(number=file.version_number)
            path = last_version.upload.path
            zf.write(path, file.get_path())
        for subdir in dir.subdirs.all():
            pack_dir(subdir)

    pack_dir(dir)

    zf.close()

    with open(zf.filename, "rb") as F:
        content = F.read()

    response = HttpResponse(content, content_type="application/zip")
    response['Content-Disposition'] = bytes('attachment; filename="{}.zip"'.format(dir.name), 'utf-8')
    return response
