from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from apps.projects.models import Contributor, Project
from apps.files_management.models import FileVersion
from .models import AnnotatingXmlContent


class AnnotatorConsumer(WebsocketConsumer):
    def connect(self):
        room_symbol = get_room_symbol(self.scope)
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

        contributor = Contributor.objects.filter(project_id=project_id, user_id=self.scope['user'].pk)
        if not contributor:
            response = {
                'status': 403,
                'message': "You aren't contributor in project with id: {}.".format(project_id),
                'xml_content': None,
            }

            response = json.dumps(response)
            self.send(text_data=response)
            return

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

    # Recieve message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        if text_data == '"heartbeat"':
            # TODO: Put user presence code here
            print(text_data)
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


def get_room_symbol(scope):
    room_symbol = scope['path'].strip('/').split('/')[-1]

    return room_symbol
