from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models

from apps.files_management.models import File, FileVersion
from apps.projects.models import Project, ProjectVersion


class Entity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    xml_id = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name="created_entities", on_delete=models.SET_NULL, null=True)
    created_in_version = models.IntegerField()
    deleted_on = models.DateTimeField(null=True)
    deleted_in_version = models.IntegerField(null=True)
    deleted_by = models.ForeignKey(User, related_name="deleted_entities", default=None, on_delete=models.SET_NULL,
                                   null=True)
    type = models.CharField(max_length=255)

    class Meta:
        unique_together = ("file", "xml_id")


class EntityVersion(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    fileversion = models.ForeignKey(FileVersion, on_delete=models.CASCADE)
    name = models.TextField()
    xml = models.TextField(blank=True, null=True)
    context = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("fileversion", "entity")
        abstract = True


class PersonVersion(EntityVersion):
    forename = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)


class EventVersion(EntityVersion):
    when = models.DateTimeField(blank=True, null=True)


class OrganizationVersion(EntityVersion):
    pass


class PlaceVersion(EntityVersion):
    location = PointField(geography=True, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)


class CertaintyVersion(EntityVersion):
    pass


class ObjectVersion(EntityVersion):
    pass


class Commit(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def save(self, *args, **kwargs):
        from apps.projects.helpers import create_new_project_version

        created = self.pk is None
        super(Commit, self).save(*args, **kwargs)

        if created:
            project = self.project
            create_new_project_version(project=project, commit=self)


class Clique(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    asserted_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name="cliques", on_delete=models.SET_NULL, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_in_commit = models.ForeignKey(Commit, related_name="cliques", default=None, null=True, blank=True,
                                          on_delete=models.CASCADE)
    created_in_annotator = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, related_name="deleted_cliques", default=None, on_delete=models.SET_NULL,
                                   null=True)
    deleted_on = models.DateTimeField(null=True)
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE)


class Unification(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, related_name="unifications", on_delete=models.CASCADE)
    clique = models.ForeignKey(Clique, related_name="unifications", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_in_commit = models.ForeignKey(Commit, related_name="unifications", default=None, null=True, blank=True,
                                          on_delete=models.CASCADE)
    created_in_file_version = models.ForeignKey(FileVersion, related_name="unifications", on_delete=models.CASCADE)
    created_in_annotator = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, related_name="deleted_unifiactions", default=None, on_delete=models.SET_NULL,
                                   null=True)
    deleted_on = models.DateTimeField(null=True)
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE)
    deleted_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, blank=True,
                                                on_delete=models.CASCADE)
    ana = models.TextField(default='')
    certainty = models.CharField(max_length=255)
    description = models.TextField(default='')
    xml_id = models.CharField(max_length=255)


class CliqueToDelete(models.Model):
    clique = models.ForeignKey(Clique, on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_on = models.DateTimeField(auto_now=True)
    project_version = models.ForeignKey(ProjectVersion, on_delete=models.CASCADE)


class UnificationToDelete(models.Model):
    unification = models.ForeignKey(Unification, on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_on = models.DateTimeField(auto_now=True)
    project_version = models.ForeignKey(ProjectVersion, on_delete=models.CASCADE)


class Certainty(models.Model):
    ana = models.CharField(max_length=255)
    locus = models.CharField(max_length=255)
    cert = models.CharField(max_length=255)
    asserted_value = models.CharField(max_length=255, null=True)
    resp = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    xml_id = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    unification = models.ForeignKey(Unification, related_name='certainties', on_delete=models.CASCADE)
