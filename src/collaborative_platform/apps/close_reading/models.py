from django.db import models


class AnnotatingXmlContent(models.Model):
    file_symbol = models.CharField(max_length=255)
    xml_content = models.TextField()
