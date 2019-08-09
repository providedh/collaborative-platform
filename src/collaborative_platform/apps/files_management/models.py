import hashlib
from os.path import join
from shutil import copyfile

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet

from apps.projects.models import Project
from collaborative_platform.settings import MEDIA_ROOT

UPLOADED_FILES_PATH = 'uploaded_files/'


class FileNode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    class Meta:
        abstract = True

    def move_to(self, directory):  # type: (FileNode, Directory) -> FileNode
        self.parent_dir = directory
        self.save()
        return self


class Directory(FileNode):
    parent_dir = models.ForeignKey("Directory", related_name='subdirs', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = ("parent_dir", "name")

    def create_subdirectory(self, name):  # type: (Directory, str) -> Directory
        d = Directory(name=name, project=self.project, parent_dir=self)
        d.save()
        return d

    def rename(self, new_name):  # type: (Directory, str) -> Directory
        self.name = new_name
        self.save()

    def get_files(self):  # type: (Directory) -> QuerySet
        return self.files.values()

    def get_subdirectories(self):  # type: (Directory) -> QuerySet
        return self.subdirs.values()

    def get_content(self):  # type: (Directory) -> list
        return list(self.subdirs.order_by('name').values()) + list(self.files.order_by('name').values())


class File(FileNode):
    version_number = models.PositiveIntegerField()
    parent_dir = models.ForeignKey("Directory", related_name='files', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = ("parent_dir", "name")

    def rename(self, new_name):  # type: (File, str) -> File
        current_version = self.versions.filter(number=self.version_number).get()
        old_path = join(MEDIA_ROOT, UPLOADED_FILES_PATH, current_version.hash)
        with open(old_path) as F:
            contents = F.read()
        hashed = bytes(new_name, encoding='utf8') + \
                 bytes(str(self.project_id), encoding='utf8') + \
                 bytes(str(self.parent_dir_id), encoding='utf8') + \
                 bytes(contents, encoding='utf-8')
        hash = hashlib.sha512(hashed).hexdigest()

        new_path = join(MEDIA_ROOT, UPLOADED_FILES_PATH, hash)
        copyfile(old_path, new_path)

        fv = FileVersion(upload=new_path, hash=hash, file=self, number=current_version.number + 1)
        fv.save()

        self.version_number += 1
        self.name = new_name
        self.save()


class FileVersion(models.Model):
    upload = models.FileField(upload_to=UPLOADED_FILES_PATH)
    hash = models.CharField(max_length=128, primary_key=True)
    file = models.ForeignKey(File, related_name='versions', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_fileversions', null=True,
                                   blank=True)

    class Meta:
        unique_together = ("file", "number")
