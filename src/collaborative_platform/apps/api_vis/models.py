from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models

from apps.files_management.models import File, FileVersion
from apps.projects.models import Project


class Entity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    xml_id = models.CharField(max_length=255)
    added_in_version = models.IntegerField()
    deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True)
    deleted_in_version = models.IntegerField(null=True)
    type = models.CharField(max_length=12)

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
    date = models.DateTimeField(blank=True, null=True)


class OrganizationVersion(EntityVersion):
    pass


class PlaceVersion(EntityVersion):
    location = PointField(geography=True, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)


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
            create_new_project_version(project=project, new_commit=self)


class Clique(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    asserted_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name="cliques", on_delete=models.SET_NULL, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_in_commit = models.ForeignKey(Commit, related_name="cliques", default=None, null=True, blank=True,
                                          on_delete=models.CASCADE)
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
    deleted_by = models.ForeignKey(User, related_name="deleted_unifiactions", default=None, on_delete=models.SET_NULL,
                                   null=True)
    deleted_on = models.DateTimeField(null=True)
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE)
    certainty = models.CharField(max_length=10)


class CliquesToDelete(models.Model):
    clique = models.ForeignKey(Clique, on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_on = models.DateTimeField(auto_now=True)


class UnificationToDelete(models.Model):
    unification = models.ForeignKey(Unification, on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_on = models.DateTimeField(auto_now=True)
