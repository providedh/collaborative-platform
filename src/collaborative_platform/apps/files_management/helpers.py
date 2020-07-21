import hashlib
import logging
import re
import time

from io import BytesIO
from json import loads

from typing import Set

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils import timezone

import apps.index_and_search.models as es

from apps.files_management.models import File, FileVersion, Directory, FileMaxXmlIds
from apps.index_and_search.models import Person, Organization, Event, Place, Ingredient, Utensil, ProductionMethod
from apps.projects.helpers import log_activity
from apps.projects.models import Project

logger = logging.getLogger('upload')

ALL_ES_ENTITIES = (Person, Organization, Event, Place, Ingredient, Utensil, ProductionMethod, es.File)


def upload_file(uploaded_file, project, user, parent_dir=None):  # type: (UploadedFile, Project, User, int) -> File
    # I assume that the project exists, bc few level above we checked if user has permissions to write to it.

    st = time.time()
    try:
        File.objects.get(name=uploaded_file.name, parent_dir_id=parent_dir, project=project, deleted=False)
        t = time.time()
        logger.info(f"Got File object from DB in {round(t - st, 2)} s")
    except File.DoesNotExist:
        dbfile = File(name=uploaded_file.name, parent_dir_id=parent_dir, project=project, version_number=1)
        dbfile.save()
        t = time.time()
        logger.info(f"Created and saved new file object to DB in {round(t - st, 2)} s")

        try:
            st = time.time()
            hash = hash_file(dbfile, uploaded_file)
            t = time.time()
            logger.info(f"Hashed file info in {round(t - st, 2)} s")
            uploaded_file.name = hash
            st = time.time()
            file_version = FileVersion(upload=uploaded_file, number=1, hash=hash, file=dbfile, created_by=user)
            file_version.save()
            FileMaxXmlIds(file=dbfile).save()
            t = time.time()
            logger.info(f"Created and saved Fv and XMLMaxIDs to DB in {round(t - st, 2)} s")
        except Exception as e:
            dbfile.delete()
            raise e
        else:
            log_activity(project, user, "created", file=dbfile)
            return dbfile
    else:
        raise FileExistsError(f"File with name {uploaded_file.name} already exist in this directory")


def overwrite_file(dbfile, uploaded_file, user):  # type: (File, UploadedFile, User) -> File
    hash = hash_file(dbfile, uploaded_file)
    latest_file_version = dbfile.file_versions.filter(number=dbfile.version_number).get()  # type: FileVersion
    if latest_file_version.hash == hash:
        return dbfile  # current file is the same as uploaded one

    uploaded_file.name = hash
    new_version_number = latest_file_version.number + 1
    new_file_version = FileVersion(upload=uploaded_file, number=new_version_number, hash=hash, file=dbfile,
                                   created_by=user, creation_date=timezone.now())

    dbfile.version_number = new_version_number
    dbfile.save()

    try:
        new_file_version.save()
    except:
        dbfile.version_number -= 1
        dbfile.save()

    log_activity(dbfile.project, user, action_text="created version number {} of".format(new_version_number),
                 file=dbfile)
    return dbfile


def hash_file(dbfile, uploaded_file):  # type: (File, UploadedFile) -> str
    uploaded_file.seek(0)
    hashed = bytes(uploaded_file.name, encoding='utf8') + \
             bytes(str(dbfile.project_id), encoding='utf8') + \
             bytes(str(dbfile.parent_dir_id), encoding='utf8') + \
             uploaded_file.read()
    hash = hashlib.sha512(hashed).hexdigest()
    return hash


def create_uploaded_file_object_from_string(string, file_name):  # type: (str, str) -> UploadedFile
    file = BytesIO(string.encode('utf-8'))

    uploaded_file = UploadedFile(file=file, name=file_name)

    return uploaded_file


def get_directory_content(dir, indent):  # type: (Directory, int) -> dict
    files = list(map(model_to_dict, dir.files.filter(deleted=False)))
    for file in files:
        file['kind'] = 'file'
        file['icon'] = 'fa-file-xml-o'
        file['open'] = False
        file['parent'] = dir.id
        file['indent'] = indent + 1

    subdirs = [get_directory_content(subdir, indent + 1) for subdir in dir.subdirs.filter(deleted=False)]

    result = model_to_dict(dir)
    result['parent'] = dir.parent_dir_id or 0
    result['children'] = files + subdirs
    result['kind'] = "folder"
    result['icon'] = 'fa-file-folder-o'
    result['open'] = not indent
    result['show'] = not indent
    result['indent'] = indent

    return result


def get_all_child_dirs(directory):  # type: (Directory) -> Set[int]
    children = set()

    for child in directory.subdirs.all():
        children.add(child.id)
        children.update(get_all_child_dirs(child))

    return children


def is_child(parent, child):  # type: (int, int) -> bool
    parent_dir = Directory.objects.get(id=parent, deleted=False)
    children = get_all_child_dirs(parent_dir)
    return child in children


def include_user(response):  # type: (JsonResponse) -> JsonResponse
    json = loads(response.content)
    for fv in json['data']:
        u = User.objects.get(id=fv['created_by_id'])  # type: User
        fv['created_by'] = u.first_name + ' ' + u.last_name

    return JsonResponse(json)


def delete_es_docs(file_id):  # type: (int) -> None
    for entity_model in ALL_ES_ENTITIES:
        entity_model.search().filter('term', file_id=file_id).delete()


def delete_directory_with_contents_fake(directory_id, user):  # type: (int, User) -> None
    child_directories = Directory.objects.filter(parent_dir=directory_id, deleted=False)

    for directory in child_directories:
        delete_directory_with_contents_fake(directory_id=directory.id, user=user)

    files = File.objects.filter(parent_dir=directory_id, deleted=False)

    for file in files:
        file.delete_fake(user)
        log_activity(project=file.project, user=user, action_text=f"deleted file {file.name}")

    directory = Directory.objects.get(id=directory_id)
    directory.delete_fake()
    log_activity(project=directory.project, user=user, related_dir=directory,
                 action_text=f"deleted directory {directory.name}")


def clean_name(name):
    name = re.sub(r'[^a-zA-Z0-9\-_]', '_', name)

    return name
