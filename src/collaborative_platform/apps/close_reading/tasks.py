from __future__ import unicode_literals

import logging

from celery import shared_task
from datetime import datetime, timezone

from .models import AnnotatingBodyContent, Operation, RoomPresence


logger = logging.getLogger('celery')


@shared_task(name='close_reading.tasks.prune_presence')
def prune_presence():
    room_presences = RoomPresence.objects.all()

    for presence in room_presences:
        time_delta = datetime.now(timezone.utc) - presence.timestamp

        if time_delta.total_seconds() > 60:
            presence.delete()

            logger.info(f"User: '{presence.user.username}' removed from 'room_presence' table due to inactivity")

            remain_users = RoomPresence.objects.filter(room_symbol=presence.room_symbol)

            logger.info(f"In room: '{presence.room_symbol}' left: {len(remain_users)} users")


@shared_task(name='close_reading.tasks.prune_orphaned_annotating_body_contents')
def prune_orphaned_annotating_body_contents():
    room_presences = RoomPresence.objects.all()
    annotating_body_contents = AnnotatingBodyContent.objects.all()

    active_room_symbols = set()

    for presence in room_presences:
        active_room_symbols.add(presence.room_symbol)

    for body_content in annotating_body_contents:
        file_id = body_content.file_symbol.split('_')[-1]
        operations = Operation.objects.filter(file_id=file_id)

        if body_content.file_symbol not in active_room_symbols and not operations:
            body_content.delete()

            logger.info(f"Content of <body> element of file: '{body_content.file_name}' removed from room: "
                        f"'{body_content.file_symbol}'")
