from __future__ import unicode_literals
from celery import shared_task
from channels_presence.models import Room
from .models import AnnotatingXmlContent


@shared_task(name='close_reading.tasks.prune_orphaned_annotating_xml_contents')
def prune_orphaned_annotating_xml_contents():
    active_rooms = Room.objects.all()
    annotating_xml_contents = AnnotatingXmlContent.objects.all()

    active_rooms_symbols = []

    for room in active_rooms:
        active_rooms_symbols.append(room.channel_name)

    for xml_content in annotating_xml_contents:
        if xml_content.file_symbol not in active_rooms_symbols:
            xml_content.delete()
