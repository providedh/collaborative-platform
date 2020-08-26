from __future__ import unicode_literals

from celery import shared_task
from datetime import datetime, timezone

from apps.close_reading.loggers import CloseReadingLogger

from .models import AnnotatingBodyContent, Operation, RoomPresence


@shared_task(name='close_reading.tasks.prune_presence')
def prune_presence():
    room_presences = RoomPresence.objects.all()

    for presence in room_presences:
        time_delta = datetime.now(timezone.utc) - presence.timestamp

        if time_delta.total_seconds() > 60:
            presence.delete()

            CloseReadingLogger().log_removing_user_from_room_presence_table(presence.user.id, inactivity=True)

            remain_users = RoomPresence.objects.filter(room_symbol=presence.room_symbol)

            CloseReadingLogger().log_number_of_remaining_users_in_room(presence.room_symbol, remain_users.count())


@shared_task(name='close_reading.tasks.prune_orphaned_annotating_body_contents')
def prune_orphaned_annotating_body_contents():
    room_presences = RoomPresence.objects.all()
    annotating_body_contents = AnnotatingBodyContent.objects.all()

    active_room_symbols = set()

    for presence in room_presences:
        active_room_symbols.add(presence.room_symbol)

    for body_content in annotating_body_contents:
        file_id = body_content.room_symbol.split('_')[-1]
        operations = Operation.objects.filter(file_id=file_id)

        if body_content.room_symbol not in active_room_symbols and not operations:
            body_content.delete()

            CloseReadingLogger().log_pruning_body_content(body_content.file.id, body_content.room_symbol)
