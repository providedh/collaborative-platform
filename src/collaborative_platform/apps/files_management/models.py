import hashlib

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Q
from django.http import HttpResponse

from apps.projects.models import Project, ProjectVersion


UPLOADED_FILES_PATH = 'uploaded_files/'


class FileNode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def move_to(self, directory_id):  # type: (FileNode, int) -> FileNode
        self.parent_dir_id = directory_id
        self.save()
        return self

    def get_path(self):
        s = self
        r = [self.name]
        while s.parent_dir is not None:
            r.insert(0, s.parent_dir.name)
            s = s.parent_dir

        return '/'.join(r)

    def delete_fake(self, user=None):
        self.deleted = True
        self.deleted_on = datetime.now()
        self.save()


class Directory(FileNode):
    parent_dir = models.ForeignKey("Directory", related_name='subdirs', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent_dir', 'name'], name='unique_undeleted_directory', condition=Q(deleted=False))
        ]

    def create_subdirectory(self, name, user):  # type: (Directory, str, User) -> Directory
        from apps.projects.helpers import log_activity

        d = Directory(name=name, project=self.project, parent_dir=self)
        d.save()
        log_activity(project=d.project, user=user, related_dir=d,
                     action_text="created directory {} in {}".format(d.name, self.name))
        return d

    def rename(self, new_name, user):  # type: (Directory, str, User) -> Directory
        from apps.projects.helpers import log_activity
        old_name = self.name
        self.name = new_name
        self.save()
        log_activity(project=self.project, user=user, related_dir=self,
                     action_text="renamed directory {} to {}".format(old_name, new_name))

    def get_files(self):  # type: (Directory) -> QuerySet
        return self.files.values()

    def get_subdirectories(self):  # type: (Directory) -> QuerySet
        return self.subdirs.values()

    def get_content(self):  # type: (Directory) -> list
        return list(self.subdirs.order_by('name').values()) + list(self.files.order_by('name').values())

    def move_to(self, directory_id):  # type: (FileNode, int) -> FileNode
        if self.parent_dir_id is None:
            raise ReferenceError("Cannot move parent dir!")

        if self.id == directory_id:
            raise ReferenceError("Cannot move dir into itself!")

        from apps.files_management.helpers import is_child
        if is_child(self.id, directory_id):
            raise ReferenceError("Moving parent dir to child dir is not allowed.")
        return super().move_to(directory_id)


class File(FileNode):
    version_number = models.PositiveIntegerField()
    parent_dir = models.ForeignKey("Directory", related_name='files', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent_dir', 'name'], name='unique_undeleted_file', condition=Q(deleted=False))
        ]

    def rename(self, new_name, user):  # type: (File, str, User) -> File
        from apps.files_management.helpers import create_uploaded_file_object_from_string
        from apps.projects.helpers import log_activity

        old_name = self.name
        if old_name == new_name:
            return

        current_version = self.file_versions.filter(number=self.version_number).get()
        contents = current_version.get_raw_content()

        hashed = bytes(new_name, encoding='utf8') + \
                 bytes(str(self.project_id), encoding='utf8') + \
                 bytes(str(self.parent_dir_id), encoding='utf8') + \
                 bytes(contents, encoding='utf-8')
        hash = hashlib.sha512(hashed).hexdigest()

        uf = create_uploaded_file_object_from_string(contents, hash)
        fv = FileVersion(upload=uf, hash=hash, file=self, number=current_version.number + 1, created_by=user)
        fv.save()

        self.version_number += 1
        self.name = new_name
        self.save()
        log_activity(project=self.project, user=user, file=self,
                     action_text="renamed {} to".format(old_name))

    def get_rendered_content(self):
        file_version = self.file_versions.get(number=self.version_number)
        content = file_version.get_rendered_content()

        return content

    def delete(self, using=None, keep_parents=False):
        from apps.files_management.helpers import delete_es_docs
        delete_es_docs(self.id)
        super().delete()

    def get_relative_path(self):
        path = self.name
        parent_dir = self.parent_dir

        while parent_dir is not None:
            path = parent_dir.name + '/' + path
            parent_dir = parent_dir.parent_dir

        return path

    def delete_fake(self, user=None):
        if not user:
            raise ValueError("Attribute 'user' is required to delete a file.")

        from apps.projects.helpers import create_new_project_version
        from apps.files_management.helpers import delete_es_docs

        delete_es_docs(self.id)

        super().delete_fake()

        deleted_entities_ids = self.__fake_delete_entities(user)
        commit = self.__fake_delete_unifications(user, deleted_entities_ids)

        create_new_project_version(project=self.project, files_modification=True, commit=commit)

    def __fake_delete_entities(self, user):
        from apps.api_vis.models import Entity

        entities = Entity.objects.filter(
            file=self,
            deleted_in_file_version__isnull=True,
        )

        deleted_entities_ids = []

        for entity in entities:
            entity.delete_fake(user)
            deleted_entities_ids.append(entity.id)

        return deleted_entities_ids

    def __fake_delete_unifications(self, user, deleted_entities_ids):
        from apps.api_vis.models import Commit, Unification

        unifications = Unification.objects.filter(
            entity_id__in=deleted_entities_ids,
            deleted_on__isnull=True,
        )

        if unifications:
            commit = Commit.objects.create(
                project=self.project,
                message=f"Removing unifications associated with deleted file '{self.name}'.",
            )

            for unification in unifications:
                unification.delete_fake(user, commit)

            return commit


class FileVersion(models.Model):
    upload = models.FileField(upload_to=UPLOADED_FILES_PATH, null=True)
    hash = models.CharField(max_length=255, null=True)
    file = models.ForeignKey(File, related_name='file_versions', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='file_versions', null=True,
                                   blank=True)
    message = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = ("file", "number")

    def get_raw_content(self):
        self.upload.open(mode='r')
        content = self.upload.read()
        self.upload.close()
        return content

    def get_raw_content_binary(self):
        self.upload.open(mode='rb')
        content_binary = self.upload.read()
        self.upload.close()
        return content_binary

    def get_rendered_content(self):
        from apps.files_management.file_conversions.file_renderer import FileRenderer

        file_renderer = FileRenderer()
        content = file_renderer.render_file_version(self)

        return content

    def save(self, *args, **kwargs):
        from apps.projects.helpers import create_new_project_version

        created = self.pk is None
        super(FileVersion, self).save(*args, **kwargs)

        if created:
            project = self.file.project
            create_new_project_version(project=project, files_modification=True)


class FileMaxXmlIds(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    xml_id_base = models.CharField(max_length=255)
    xml_id_number = models.IntegerField(default=0)

    def get_next_number(self):
        xml_id_number = self.xml_id_number

        self.xml_id_number += 1
        self.save()

        return xml_id_number
