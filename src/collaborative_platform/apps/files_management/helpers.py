import hashlib
from io import BytesIO
from typing import List

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.forms import model_to_dict
from django.utils import timezone

from apps.index_and_search.content_extractor import ContentExtractor
from apps.index_and_search.entities_extractor import EntitiesExtractor
from apps.index_and_search.models import Person, Organization, Event, Place
from apps.projects.helpers import log_activity
from apps.files_management.models import File, FileVersion, Project, Directory


def upload_new_file(uploaded_file, project, parent_dir, user):  # type: (UploadedFile, Project, int, User) -> File
    # I assume that the project exists, bc few level above we checked if user has permissions to write to it.

    dbfile = File(name=uploaded_file.name, parent_dir_id=parent_dir, project=project, version_number=1)
    dbfile.save()

    try:
        hash = hash_file(dbfile, uploaded_file)
        uploaded_file.name = hash
        file_version = FileVersion(upload=uploaded_file, number=1, hash=hash, file=dbfile, created_by=user)
        file_version.save()
    except Exception as e:
        dbfile.delete()
        raise e
    else:
        log_activity(project, user, "created", file=dbfile)
        return dbfile


def overwrite_existing_file(dbfile, uploaded_file, user):  # type: (File, UploadedFile, User) -> File
    hash = hash_file(dbfile, uploaded_file)
    latest_file_version = dbfile.versions.filter(number=dbfile.version_number).get()  # type: FileVersion
    if latest_file_version.hash == hash:
        return dbfile  # current file is the same as uploaded one

    uploaded_file.name = hash
    new_version_number = latest_file_version.number + 1
    new_file_version = FileVersion(upload=uploaded_file, number=new_version_number, hash=hash, file=dbfile,
                                   created_by=user, creation_date=timezone.now())
    new_file_version.save()

    dbfile.version_number = new_version_number
    dbfile.save()

    log_activity(dbfile.project, user, action_text="created version number () of".format(new_version_number),
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


def upload_file(uploaded_file, project, user, parent_dir=None):  # type: (UploadedFile, Project, User, int) -> File
    try:
        dbfile = File.objects.filter(name=uploaded_file.name, parent_dir_id=parent_dir, project=project).get()
    except File.DoesNotExist:
        return upload_new_file(uploaded_file, project, parent_dir, user)
    else:
        return overwrite_existing_file(dbfile, uploaded_file, user)


def uploaded_file_object_from_string(string, file_name):  # type: (str, str) -> UploadedFile
    file = BytesIO(string.encode('utf-8'))

    uploaded_file = UploadedFile(file=file, name=file_name)

    return uploaded_file


def extract_text_and_entities(contents, project_id, file_id):  # type: (str, int, int) -> (str, List[dict])
    if len(contents) == 0:
        return "", []
    text = ContentExtractor.tei_contents_to_text(contents)
    entities = EntitiesExtractor.extract_entities(contents)
    entities = EntitiesExtractor.extend_entities(entities, project_id, file_id)
    return text, entities


def index_entities(entities):  # type: (List[dict]) -> None
    classes = {
        'person': Person,
        'org': Organization,
        'event': Event,
        'place': Place
    }

    for entity in entities:
        tag = entity.pop('tag')
        es_entity = classes[tag](**entity)
        es_entity.save()


def get_directory_content(dir, indent):  # type: (Directory, int) -> dict
    files = list(map(model_to_dict, dir.files.all()))
    for file in files:
        file['kind'] = 'file'
        file['icon'] = 'fa-file-xml-o'
        file['open'] = False
        file['parent'] = dir.id
        file['indent'] = indent + 1

    subdirs = [get_directory_content(subdir, indent + 1) for subdir in dir.subdirs.all()]

    result = model_to_dict(dir)
    result['parent'] = dir.parent_dir_id or 0
    result['children'] = files + subdirs
    result['kind'] = "folder"
    result['icon'] = 'fa-file-folder-o'
    result['open'] = not indent
    result['indent'] = indent

    return result
