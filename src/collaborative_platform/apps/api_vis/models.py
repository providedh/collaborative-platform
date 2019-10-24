from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models

from apps.files_management.models import File, FileVersion
from apps.projects.models import Project


class Entity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    fileversion = models.ForeignKey(FileVersion, on_delete=models.CASCADE)
    xml_id = models.CharField(max_length=255)
    name = models.TextField()
    xml = models.TextField(blank=True, null=True)
    context = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=12)

    class Meta:
        unique_together = ("fileversion", "id")


class Person(Entity):
    forename = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)


class Event(Entity):
    date = models.DateTimeField()


class Organization(Entity):
    pass


class Place(Entity):
    location = PointField(geography=True, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)


class Commit(models.Model):
    fileversions = models.ManyToManyField(FileVersion, related_name="commits")
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()


class Clique(models.Model):
    asserted_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name="cliques", on_delete=models.SET_NULL, blank=True, null=True)
    commit = models.ForeignKey(Commit, related_name="cliques", default=None, null=True, blank=True,
                               on_delete=models.SET_NULL)


class Unification(models.Model):
    entity = models.ForeignKey(Entity, related_name="unifications", on_delete=models.DO_NOTHING)
    clique = models.ForeignKey(Clique, related_name="unifications", on_delete=models.DO_NOTHING)
    made_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    made_on = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey(User, related_name="deleted_unifiactions", default=None, on_delete=models.DO_NOTHING, null=True)
    deleted_on = models.DateTimeField(null=True)
    levenshtein = models.IntegerField()
    certainty = models.CharField(max_length=10)
    commit = models.ForeignKey(Commit, related_name="unifications", default=None, null=True, blank=True,
                               on_delete=models.SET_NULL)
