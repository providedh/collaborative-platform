from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from datetime import datetime, timezone

from apps.projects.models import Contributor, Project
from apps.files_management.models import FileVersion
from .models import AnnotatingXmlContent, RoomPresence



class AnnotatorConsumer(WebsocketConsumer):
    def connect(self):
        room_symbol = self.scope['url_route']['kwargs']['room_name']
        project_id, file_id = room_symbol.split('_')

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            response = {
                'status': 404,
                'message': "Project with id: {} doesn't exist.".format(project_id),
                'xml_content': None,
            }

            response = json.dumps(response)
            self.send(text_data=response)
            return

        # COMMENTED FOR SIMPLE WEBSOCKET CLIENT (TO BYPASS NOT WORKING JS IN CLOSE READING APP)
        # contributor = Contributor.objects.filter(project_id=project_id, user_id=self.scope['user'].pk)
        # if not contributor:
        #     response = {
        #         'status': 403,
        #         'message': "You aren't contributor in project with id: {}.".format(project_id),
        #         'xml_content': None,
        #     }
        #
        #     response = json.dumps(response)
        #     self.send(text_data=response)
        #     return

        try:
            annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)

        except AnnotatingXmlContent.DoesNotExist:
            try:
                file = FileVersion.objects.filter(file_id=file_id).order_by('-number')[0]
            except FileVersion.DoesNotExist:
                response = {
                    'status': 404,
                    'message': 'File not found.',
                    'xml_content': None,
                }

                response = json.dumps(response)
                self.send(text_data=response)
                return

            with open(file.upload.path) as file:
                xml_content = file.read()

                annotating_xml_content = AnnotatingXmlContent(file_symbol=room_symbol, xml_content=xml_content)
                annotating_xml_content.save()

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'close_reading_{}'.format(self.room_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        room_presence, created = RoomPresence.objects.get_or_create(
            room_symbol=room_symbol,
            user=self.scope['user'],
        )

        room_presence.save()

        response = {
            'status': 200,
            'message': 'OK',
            'xml_content': annotating_xml_content.xml_content,
        }

        response = json.dumps(response)

        self.send(text_data=response)

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        room_symbol = self.scope['url_route']['kwargs']['room_name']

        room_presence = RoomPresence.objects.get(
            room_symbol=room_symbol,
            user=self.scope['user'],
        )

        room_presence.delete()

        remain_users = RoomPresence.objects.filter(room_symbol=room_symbol)

        if not remain_users:
            AnnotatingXmlContent.objects.get(file_symbol=room_symbol).delete()


    # Recieve message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        room_symbol = self.scope['url_route']['kwargs']['room_name']

        if text_data == '"heartbeat"':
            room_presence = RoomPresence.objects.get(
                room_symbol=room_symbol,
                user=self.scope['user'],
            )

            room_presence.save()

        else:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    # Recieve message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
