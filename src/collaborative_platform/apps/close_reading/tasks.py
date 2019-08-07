from __future__ import unicode_literals
from celery import shared_task
from datetime import datetime, timezone

from .models import AnnotatingXmlContent, RoomPresence


@shared_task(name='close_reading.tasks.prune_presence')
def prune_presence():
    room_presences = RoomPresence.objects.all()

    for presence in room_presences:
        time_delta = datetime.now(timezone.utc) - presence.timestamp

        if time_delta.total_seconds() > 60:
            presence.delete()


@shared_task(name='close_reading.tasks.prune_orphaned_annotating_xml_contents')
def prune_orphaned_annotating_xml_contents():
    room_presences = RoomPresence.objects.all()
    annotating_xml_contents = AnnotatingXmlContent.objects.all()

    active_room_symbols = set()

    for presence in room_presences:
        active_room_symbols.add(presence.room_symbol)

    for xml_content in annotating_xml_contents:
        if xml_content.file_symbol not in active_room_symbols:
            xml_content.delete()
