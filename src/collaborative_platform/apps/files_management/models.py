from django.db import models

from apps.projects.models import Project


class FileNode(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    parent_dir = models.ForeignKey("Directory", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        abstract = True


class Directory(FileNode):
    class Meta:
        unique_together = ("parent_dir", "name")


class File(FileNode):
    version_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ("parent_dir", "name")


class FileVersion(models.Model):
    upload = models.FileField(upload_to='uploaded_files/')
    hash = models.CharField(max_length=128, primary_key=True)
    file = models.ForeignKey(File, related_name='versions', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("file", "number")
