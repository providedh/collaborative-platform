from django.db import models
from django.contrib.auth.models import User


class AnnotatingXmlContent(models.Model):
    file_symbol = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    xml_content = models.TextField()


class RoomPresence(models.Model):
    room_symbol = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
