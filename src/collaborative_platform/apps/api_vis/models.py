from django.contrib.gis.db.models import PointField
from django.db import models

from apps.files_management.models import File, FileVersion
from apps.projects.models import Project


class Entity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    fileversion = models.ForeignKey(FileVersion, on_delete=models.CASCADE)
    id = models.CharField(max_length=255)
    name = models.TextField()
    xml = models.TextField()
    context = models.TextField()

    class Meta:
        abstract = True
        unique_together = ("fileversion", "id")


class Person(Entity):
    forename = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)


class Event(Entity):
    date = models.DateTimeField()


class Organization(Entity):
    pass


class Place(Entity):
    location = PointField(geography=True)
    country = models.CharField(max_length=255)
