from django.db import models

from ..projects.models import Project


class FileNode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    parent_dir = models.ForeignKey("Folder", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        abstract = True


class Folder(FileNode):
    class Meta:
        unique_together = ("parent_dir", "name")


class File(FileNode):
    version_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ("parent_dir", "name", "version_number")


class FileVersion(models.Model):
    upload = models.FileField(upload_to='files/')
    hash = models.CharField(max_length=40, primary_key=True, unique=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
