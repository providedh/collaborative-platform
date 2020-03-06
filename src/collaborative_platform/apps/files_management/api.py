import logging

import time
from json import dumps, loads
from os import mkdir
from zipfile import ZipFile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseServerError
from lxml.etree import XMLSyntaxError

# from apps.api_vis.helpers import create_entities_in_database
from apps.files_management.file_conversions.ids_filler import IDsFiller
from apps.files_management.file_conversions.ids_corrector import IDsCorrector
from apps.projects.helpers import log_activity, paginate_start_length, page_to_json_response
from apps.files_management.models import File, FileVersion, Directory
from apps.views_decorators import objects_exists, user_has_access
from .file_conversions.tei_handler import TeiHandler
from .helpers import append_unifications, extract_text_and_entities, index_entities, upload_file, \
    create_uploaded_file_object_from_string, get_directory_content, include_user, index_file, \
    delete_directory_with_contents_fake, overwrite_file, clean_name


logger = logging.getLogger('upload')


@login_required
@objects_exists
@user_has_access("RW")
def upload(request, directory_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("file")

        if not files_list:
            return HttpResponseBadRequest("File not attached properly")

        parent_dir = directory_id
        project = Directory.objects.get(id=parent_dir, deleted=False).project

        upload_statuses = []

        start_extracting = time.time()
        for i, file in enumerate(files_list):
            file_name = clean_name(file.name)
            file.name = file_name

            upload_status = {'file_name': file_name, 'uploaded': False, 'migrated': False, 'message': None}
            upload_statuses.append(upload_status)

            try:
                start_uploading = time.time()
                logger.info(f"Uploading file {file_name}: initiation done in "
                            f"{round(start_uploading - start_extracting, 2)} s")

                dbfile = upload_file(file, project, request.user, parent_dir)

                upload_status = {'uploaded': True}
                upload_statuses[i].update(upload_status)

                start_recognizing = time.time()
                logger.info(f"Uploading file {file_name}: upload done in "
                            f"{round(start_recognizing - start_uploading, 2)} s")

                file_version = FileVersion.objects.get(file_id=dbfile.id, number=dbfile.version_number)
                path_to_file = file_version.upload.path

                tei_handler = TeiHandler(path_to_file)
                migration, is_tei_p5_unprefixed = tei_handler.recognize()

                if not migration and not is_tei_p5_unprefixed:
                    upload_status = {"message": "Invalid filetype, please provide TEI file or compatible ones.",
                                     "uploaded": False}
                    upload_statuses[i].update(upload_status)
                    dbfile.activities.get().delete()
                    dbfile.delete()
                    continue

                start_migrating = time.time()
                logger.info(f"Uploading file {file_name}: migration recognizing done in "
                            f"{round(start_migrating - start_recognizing, 2)} s")

                if migration:
                    tei_handler.migrate()

                start_ids_filling = time.time()
                logger.info(f"Uploading file {file_name}: migration done in "
                            f"{round(start_ids_filling - start_migrating, 2)} s")





                try:
                    # tei_handler = IDsFiller(tei_handler, file_name, dbfile.pk)

                    ids_corrector = IDsCorrector()

                    xml_content = file_version.get_content()

                    xml_content = ids_corrector.correct_ids(xml_content, project.id)

                except XMLSyntaxError:
                    is_id_filled = False
                else:
                    is_id_filled = tei_handler.process(initial=True)







                start_extracting = time.time()
                logger.info(f"Uploading file {file_name}: filling ID's done in "
                            f"{round(start_extracting - start_ids_filling, 2)} s")

                if migration or is_id_filled:
                    migrated_string = tei_handler.text.read()

                    text, entities = extract_text_and_entities(migrated_string, project.id, dbfile.id)

                    finish_extracting = time.time()
                    logger.info(f"Uploading file {file_name}: extracted text and entities in "
                                f"{round(finish_extracting - start_extracting, 2)} s")

                    uploaded_file = create_uploaded_file_object_from_string(migrated_string, file_name)

                    dbfile = File.objects.get(name=uploaded_file.name, parent_dir_id=parent_dir, project=project,
                                              deleted=False)
                    dbfile = overwrite_file(dbfile, uploaded_file, request.user)

                    saved_ver2 = time.time()
                    logger.info(f"Uploading file {file_name}: created second fileversion in db "
                                f"{round(saved_ver2 - finish_extracting, 2)} s")

                    message = tei_handler.get_message()
                    migration_status = {'migrated': True, 'message': message}
                    upload_statuses[i].update(migration_status)
                    dt = time.time()
                    # create_entities_in_database(entities, project, file_version)
                    logger.info(f"creating entities in db took {time.time() - dt} s")
                    dt = time.time()
                    index_entities(entities)
                    index_file(dbfile, text)
                    logger.info(f"indexing entities and file in es took {time.time() - dt} s")

                    log_activity(dbfile.project, request.user, "File migrated: {} ".format(message), dbfile)

                    finish_indexing = time.time()
                    logger.info(f"Uploading file {file_name}: indexing entities done in "
                                f"{round(finish_indexing - saved_ver2, 2)} s")
                else:
                    file.seek(0)
                    text, entities = extract_text_and_entities(file.read(), project.id, dbfile.id)
                    # create_entities_in_database(entities, project, file_version)
                    index_entities(entities)
                    index_file(dbfile, text)

                    finish_indexing = time.time()
                    logger.info(f"Uploading file {file_name}: extarcted, indexed entities and filled IDs in "
                                f"{round(finish_indexing - start_extracting, 2)} s")

                logger.info(f"Uploading file {file_name}: file processing done in "
                            f"{round(finish_indexing - start_extracting, 2)} s")

            except Exception as exception:
                upload_status = {'message': str(exception)}
                upload_statuses[i].update(upload_status)

        response = dumps(upload_statuses)

        return HttpResponse(response, status=200, content_type='application/json')

    return HttpResponseBadRequest("Invalid request method or files not attached")


@login_required
@objects_exists
@user_has_access()
def get_file_versions(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)

        page = paginate_start_length(request, file.versions.all())
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
        return get_file_version(request, *args, **kwargs)


@login_required
@objects_exists
@user_has_access()
def get_file_version(request, file_id, version=None):  # type: (HttpRequest, int, int) -> HttpResponse
    file = File.objects.get(id=file_id, deleted=False)

    if version is None:
        version = file.version_number

    file_version = file.versions.filter(number=version).get()  # type: FileVersion

    try:
        creator = model_to_dict(file_version.created_by, fields=('id', 'first_name', 'last_name'))
    except (AttributeError, User.DoesNotExist):
        creator = file_version.created_by_id

    file_version.upload.open('r')
    xml_content = file_version.upload.read()
    file_version.upload.close()

    xml_content = append_unifications(xml_content, file_version)

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
        delete_directory_with_contents_fake(kwargs['directory_id'], request.user)
    elif 'file_id' in kwargs:
        file = File.objects.get(id=kwargs['file_id'], deleted=False)
        log_activity(project=file.project, user=request.user, action_text=f"deleted file {file.name}")
        file.delete_fake(request.user)
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
    return file.download()


@login_required
@objects_exists
@user_has_access()
def download_fileversion(request, file_id, version):  # type: (HttpRequest, int, int) -> HttpResponse
    fileversion = FileVersion.objects.get(file_id=file_id, number=version)
    return fileversion.download()


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
            last_version = file.versions.get(number=file.version_number)
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
