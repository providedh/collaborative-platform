from datetime import date, datetime, time

from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models

from collaborative_platform.settings import ANONYMOUS_USER_ID

from apps.api_vis.enums import TypeChoice
from apps.files_management.models import File, FileVersion
from apps.projects.models import Project, ProjectVersion, UncertaintyCategory


def get_anonymous_user():
    anonymous_user = User.objects.get(ANONYMOUS_USER_ID)

    return anonymous_user


class Entity(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    xml_id = models.CharField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user), related_name='created_entities')
    created_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='created_entities')
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user),
                                   related_name='deleted_entities')
    deleted_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='deleted_entities')

    class Meta:
        unique_together = ("file", "xml_id")

    def delete_fake(self, user):
        file_version = self.file.file_versions.order_by('-number')[0]

        self.deleted_by = user
        self.deleted_in_file_version = file_version
        self.deleted_on = datetime.now()

        self.save()


class EntityVersion(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='versions')
    file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("file_version", "entity")


class EntityProperty(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    entity_version = models.ForeignKey(EntityVersion, default=None, null=True, on_delete=models.CASCADE,
                                       related_name='properties')
    xpath = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=[(tag, tag.value) for tag in TypeChoice])

    value_str = models.CharField(max_length=255, null=True, blank=True)
    value_int = models.IntegerField(null=True)
    value_float = models.FloatField(null=True)
    value_date = models.DateField(null=True)
    value_time = models.TimeField(null=True)
    value_point = PointField(geography=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user), related_name='created_properties')
    created_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='created_properties')
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user),
                                   related_name='deleted_properties')
    deleted_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='deleted_properties')

    def set_value(self, value):
        if type(self.type) == str:
            self.type = eval(self.type)

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

    def get_value(self, as_str=False):
        if type(self.type) == str:
            self.type = eval(self.type)

        if self.type == TypeChoice.str:
            return self.value_str
        elif self.type == TypeChoice.int:
            return str(self.value_int) if as_str else self.value_int
        elif self.type == TypeChoice.float:
            return str(self.value_float) if as_str else self.value_float
        elif self.type == TypeChoice.date:
            return self.value_date.strftime('%Y-%m-%d') if as_str else self.value_date
        elif self.type == TypeChoice.time:
            return self.value_time.strftime('%H:%M:%S') if as_str else self.value_time
        elif self.type == TypeChoice.Point:
            return f'{self.value_point.coords[0]} {self.value_point.coords[1]}' if as_str else self.value_point


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
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)

    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user), related_name='created_cliques')
    created_on = models.DateTimeField(auto_now_add=True)
    created_in_commit = models.ForeignKey(Commit, default=None, null=True, on_delete=models.CASCADE,
                                          related_name='created_cliques')
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user),
                                   related_name='deleted_cliques')
    deleted_on = models.DateTimeField(null=True)
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, on_delete=models.CASCADE,
                                          related_name='deleted_cliques')


class Unification(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='unifications')
    clique = models.ForeignKey(Clique, on_delete=models.CASCADE, related_name='unifications')

    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user), related_name='created_unifications')
    created_on = models.DateTimeField(auto_now_add=True)
    created_in_file_version = models.ForeignKey(FileVersion, on_delete=models.CASCADE,
                                                related_name='created_unifications')
    created_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE,
                                          related_name='created_unifications')
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user),
                                   related_name='deleted_unifications')
    deleted_on = models.DateTimeField(null=True)
    deleted_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='deleted_unifications')
    deleted_in_commit = models.ForeignKey(Commit, default=None, null=True, blank=True, on_delete=models.CASCADE,
                                          related_name='deleted_unifications')

    categories = models.ManyToManyField(UncertaintyCategory)
    certainty = models.CharField(max_length=255)
    description = models.TextField(default='')
    xml_id = models.CharField(max_length=255)

    def delete_fake(self, user, commit):
        file_version = self.entity.file.file_versions.order_by('-number')[0]

        self.deleted_on = datetime.now()
        self.deleted_by = user
        self.deleted_in_commit = commit
        self.deleted_in_file_version = file_version

        self.save()

    def get_categories(self, as_str=False):
        if as_str:
            categories = self.categories.all()

            categories_links = [category.get_link() for category in categories]
            categories = ' '.join(categories_links)

            return categories

        else:
            categories = self.categories.all()

            return categories


class Certainty(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE)
    xml_id = models.CharField(max_length=255)
    categories = models.ManyToManyField(UncertaintyCategory)
    locus = models.CharField(max_length=255)
    certainty = models.CharField(max_length=255, null=True)
    degree = models.FloatField(null=True)
    target_xml_id = models.CharField(max_length=255)
    target_match = models.CharField(max_length=255, null=True)
    asserted_value = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET(get_anonymous_user), related_name='created_certainties')
    created_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='created_certainties')
    deleted_by = models.ForeignKey(User, default=None, null=True, on_delete=models.SET(get_anonymous_user),
                                   related_name='deleted_certainties')
    deleted_in_file_version = models.ForeignKey(FileVersion, default=None, null=True, on_delete=models.CASCADE,
                                                related_name='deleted_certainties')

    def get_categories(self, as_str=False):
        if as_str:
            categories = self.categories.all()

            categories_links = [category.get_link() for category in categories]
            categories = ' '.join(categories_links)

            return categories

        else:
            categories = self.categories.all()

            return categories
