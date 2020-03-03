import datetime
import django

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.urls import reverse


class Dashboard(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=150, null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    config = JSONField(blank=True, default=dict)
    created_on = models.DateField(default=django.utils.timezone.now)
    last_edited = models.DateField(default=django.utils.timezone.now)

    def get_absolute_url(self):
        return reverse('dashboard', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name