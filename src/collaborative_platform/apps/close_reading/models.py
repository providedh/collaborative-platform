from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

from apps.close_reading.enums import MethodChoice, TargetTypes


class AnnotatingBodyContent(models.Model):
    file_symbol = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
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
    method = models.CharField(max_length=255, choices=[(method, method.value) for method in MethodChoice])
    target_type = models.CharField(max_length=255, choices=[(target, target.value) for target in TargetTypes])
    edited_element_id = models.CharField(max_length=255)
    old_element_id = models.CharField(max_length=255, null=True)
    new_element_id = models.CharField(max_length=255, null=True)
