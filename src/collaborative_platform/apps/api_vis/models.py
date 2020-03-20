from datetime import date, time

from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models

from collaborative_platform.settings import ANONYMOUS_USER_ID

from apps.core.models import VirtualUser
from apps.files_management.models import File, FileVersion
from apps.projects.models import Project, ProjectVersion, UncertaintyCategory
from apps.api_vis.enums import TypeChoice


def get_anonymous_user():
    anonymous_user = User.objects.get(ANONYMOUS_USER_ID)

    return anonymous_user


class CommonFields(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user))
    created_in_file_version = models.ForeignKey(FileVersion, on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user))
    deleted_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Entity(CommonFields):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    xml_id = models.CharField(max_length=255)

    deleted_on = models.DateTimeField(null=True)

    class Meta:
        unique_together = ("file", "xml_id")


class EntityVersion(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    file_version = models.ForeignKey(FileVersion, on_delete=models.CASCADE)

    xml = models.TextField(blank=True, null=True)
    context = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("fileversion", "entity")


class EntityProperty(CommonFields):
    entity_version = models.ForeignKey(EntityVersion, on_delete=models.CASCADE)
    xpath = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=[(tag, tag.value) for tag in TypeChoice])

    value_str = models.CharField(max_length=255, null=True, blank=True)
    value_int = models.IntegerField(null=True)
    value_float = models.FloatField(null=True)
    value_date = models.DateField(null=True)
    value_time = models.TimeField(null=True)
    value_point = PointField(geography=True, null=True)

    def set_value(self, value):
        if self.type == TypeChoice.str:
            self.value_str = str(value)
        elif self.type == TypeChoice.int:
            self.value_int = int(value)
        elif self.type == TypeChoice.float:
            self.value_float = float(value)
        elif self.type == TypeChoice.date:
            self.value_date = date.fromisoformat(str(value))
        elif self.type == TypeChoice.time:
            self.value_time = time.fromisoformat(str(value))
        elif self.type == TypeChoice.Point:
            value = value.replace(',', ' ')
            values = value.split(' ')

            self.value_point = Point(float(values[0]), float(values[1]))

    def get_value(self):
        if self.type == TypeChoice.str:
            return self.value_str
        elif self.type == TypeChoice.int:
            return self.value_int
        elif self.type == TypeChoice.float:
            return self.value_float
        elif self.type == TypeChoice.date:
            return self.value_date
        elif self.type == TypeChoice.time:
            return self.value_time
        elif self.type == TypeChoice.Point:
            return self.value_point


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

    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user))
    created_on = models.DateTimeField(auto_now_add=True)
    created_in_commit = models.ForeignKey(Commit, default=None, null=True, on_delete=models.CASCADE)
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user))
    deleted_on = models.DateTimeField(null=True)
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, on_delete=models.CASCADE)


class Unification(CommonFields):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    clique = models.ForeignKey(Clique, on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)
    created_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE)
    deleted_on = models.DateTimeField(null=True)
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE)

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


class Certainty(CommonFields):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    xml_id = models.CharField(max_length=255)
    categories = models.ManyToManyField(UncertaintyCategory)
    locus = models.CharField(max_length=255)
    cert = models.CharField(max_length=255, null=True)
    degree = models.FloatField(null=True)
    target_xml_id = models.CharField(max_length=255)
    target_match = models.CharField(max_length=255, null=True)
    asserted_value = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
