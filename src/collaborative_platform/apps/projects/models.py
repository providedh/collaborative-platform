from django.contrib.auth.models import User
from apps.core.models import Profile
from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=150, blank=False)
    description = models.CharField(max_length=150, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
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
