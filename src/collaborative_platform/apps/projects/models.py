from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres import fields

from apps.core.models import Profile

TAXONOMY_FILES_PATH = 'taxonomy_files/'


class Project(models.Model):
    title = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    license = models.CharField(max_length=255, null=True, blank=True, default='GPL')
    public = models.BooleanField(default=False)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.title == '':
            raise ValidationError('Empty title')

    def save(self, *args, **kwargs):
        from apps.projects.helpers import create_new_project_version

        created = self.pk is None
        super(Project, self).save(*args, **kwargs)

        if created:
            create_new_project_version(project=self)


class Contributor(models.Model):
    permissions_levels = (
        ("AD", "Administrator"),
        ("RW", "Read+Write"),
        ("RO", "Read")
    )

    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='contributions', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=2, choices=permissions_levels, default="RO")

    class Meta:
        unique_together = ("project", "user")


class Activity(models.Model):
    project = models.ForeignKey(Project, related_name='activities', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    related_file = models.ForeignKey("files_management.File", related_name='activities', on_delete=models.SET_NULL,
                                     null=True, blank=True)
    related_file_name = models.CharField(max_length=255, null=True, blank=True)
    related_dir = models.ForeignKey("files_management.Directory", related_name='activities',
                                    on_delete=models.SET_NULL,
                                    null=True, blank=True)
    related_dir_name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='activities', null=True)
    user_name = models.CharField(max_length=255)
    action_text = models.CharField(max_length=255)


class ProjectVersion(models.Model):
    project = models.ForeignKey(Project, related_name="versions", on_delete=models.CASCADE)
    file_versions = models.ManyToManyField('files_management.FileVersion')
    file_version_counter = models.IntegerField(default=0)
    commit = models.ForeignKey('api_vis.Commit', on_delete=models.SET_NULL, null=True, blank=True)
    commit_counter = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'file_version_counter', 'commit_counter')

    def __str__(self):
        return f"{self.file_version_counter}.{self.commit_counter}"


class Taxonomy(models.Model):
    project = models.OneToOneField(Project, primary_key=True, related_name='taxonomy', on_delete=models.CASCADE)
    contents = models.TextField(null=True, blank=True)

    def update_contents(self):
        raise NotImplementedError


class UncertaintyCategory(models.Model):
    taxonomy = models.ForeignKey(Taxonomy, related_name="categories", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    xml_id = models.CharField(max_length=255)
    color = models.CharField(max_length=7)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=12)


class EntitySchema(models.Model):
    taxonomy = models.ForeignKey(Taxonomy, related_name="entities", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)
    icon = models.CharField(max_length=12)
    properties = fields.JSONField()
