from django.contrib.auth.models import User
from django.db import models

from apps.files_management.models import FileNode


class Project(models.Model):
    title = models.CharField(max_length=150, blank=False)
    description = models.CharField(max_length=150, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now_add=True)
    license = models.CharField(max_length=16, null=True, blank=True, default='GPL')
    public = models.BooleanField(default=False)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.title == '':
            raise ValidationError('Empty title')


class Contributor(models.Model):
    permissions_levels = (
        ("AD", "Administrator"),
        ("RW", "Read+Write"),
        ("RO", "Read")
    )

    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='contributions', on_delete=models.CASCADE)
    permissions = models.CharField(max_length=2, limit_choices_to=permissions_levels, default="RO")

    class Meta:
        unique_together = ("project", "user")


class Activity(models.Model):
    project = models.ForeignKey(Project, related_name='activities', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    related_filenode = models.ForeignKey(FileNode, related_name='activities', on_delete=models.DO_NOTHING,
                                         null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='activities')
    action_text = models.CharField()
