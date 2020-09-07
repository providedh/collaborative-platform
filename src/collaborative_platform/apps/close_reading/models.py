from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

from apps.close_reading.enums import Methods, ElementTypes
from apps.files_management.models import File


class AnnotatingBodyContent(models.Model):
    room_symbol = models.CharField(max_length=255)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    body_content = models.TextField()


class RoomPresence(models.Model):
    room_symbol = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    channel_name = models.CharField(max_length=255)


class AnnotationHistory(models.Model):
    project_id = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255)
    history = JSONField(blank=True, default=list)


class Operation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    method = models.CharField(max_length=255, choices=[(method, method.value) for method in Methods])
    element_type = models.CharField(max_length=255, choices=[(type, type.value) for type in ElementTypes])
    edited_element_id = models.CharField(max_length=255, null=True)
    old_element_id = models.CharField(max_length=255, null=True)
    new_element_id = models.CharField(max_length=255, null=True)
    operation_result = models.CharField(max_length=255, null=True)
    dependencies = models.ManyToManyField('self', symmetrical=False)
