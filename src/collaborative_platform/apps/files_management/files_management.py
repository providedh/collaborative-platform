import hashlib

from django.core.files.uploadedfile import UploadedFile

from .models import File, FileVersion, Project


def upload_new_file(uploaded_file, project, parent_dir):  # type: (UploadedFile, int, int) -> File
    # I assume that the project exists, bc few level above we checked if user has permissions to write to it.

    dbfile = File(name=uploaded_file.name, parent_dir_id=parent_dir, project_id=project, version_number=1)
    dbfile.save()

    try:
        hash = hash_file(dbfile, uploaded_file)
        uploaded_file.name = hash
        file_version = FileVersion(upload=uploaded_file, number=1, hash=hash, file=dbfile)
        file_version.save()
    except Exception as e:
        dbfile.delete()
        raise e
    else:
        return dbfile


def overwrite_existing_file(dbfile, uploaded_file):  # type: (File, UploadedFile) -> File
    hash = hash_file(dbfile, uploaded_file)
    latest_file_version = dbfile.fileversion_set.filter(number=dbfile.version_number).get()  # type: FileVersion
    if latest_file_version.hash == hash:
        return dbfile  # current file is the same as uploaded one

    uploaded_file.name = hash
    new_version_number = latest_file_version.number + 1
    new_file_version = FileVersion(upload=uploaded_file, hash=hash, file=dbfile, number=new_version_number)
    new_file_version.save()

    dbfile.version_number = new_version_number
    dbfile.save()
    return dbfile


def hash_file(dbfile, uploaded_file):  # type: (File, UploadedFile) -> str
    hashed = bytes(uploaded_file.name, encoding='utf8') + \
             bytes(str(dbfile.project_id), encoding='utf8') + \
             bytes(str(dbfile.parent_dir_id), encoding='utf8') + \
             uploaded_file.read()
    hash = hashlib.sha512(hashed).hexdigest()
    return hash


# TODO check perrmissions by decorator
def upload_file(uploaded_file, project, parent_dir=None):  # type: (UploadedFile, int, int) -> File
    try:
        dbfile = File.objects.filter(name=uploaded_file.name, parent_dir_id=parent_dir).get()
    except File.DoesNotExist:
        return upload_new_file(uploaded_file, project, parent_dir)
    else:
        return overwrite_existing_file(dbfile, uploaded_file)
