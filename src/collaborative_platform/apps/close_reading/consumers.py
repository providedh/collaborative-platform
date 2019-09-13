import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from apps.projects.models import Contributor, Project
from apps.files_management.models import FileVersion, File
from .models import AnnotatingXmlContent, RoomPresence
from .annotator import Annotator, NotModifiedException


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
                file_version = FileVersion.objects.filter(file_id=file_id).order_by('-number')[0]
            except FileVersion.DoesNotExist:
                response = {
                    'status': 404,
                    'message': 'File not found.',
                    'xml_content': None,
                }

                response = json.dumps(response)
                self.send(text_data=response)
                return

            file = File.objects.get(id=file_version.file_id)

            with open(file_version.upload.path) as file_version:
                xml_content = file_version.read()
                file_name = file.name

                annotating_xml_content = AnnotatingXmlContent(file_symbol=room_symbol, file_name=file_name,
                                                              xml_content=xml_content)
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

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        room_symbol = self.scope['url_route']['kwargs']['room_name']

        if text_data == '"heartbeat"':
            if self.scope['user'].pk is not None:
                room_presence = RoomPresence.objects.get(
                    room_symbol=room_symbol,
                    user=self.scope['user'],
                )

                room_presence.save()

        else:
            request_json = text_data

            annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
            xml_content = annotating_xml_content.xml_content

            user_id = self.scope['user'].pk

            request_json = json.loads(request_json)

            try:
                annotator = Annotator()
                xml_content = annotator.add_annotation(xml_content, request_json, user_id)

                annotating_xml_content.xml_content = xml_content
                annotating_xml_content.save()

                response = {
                    'status': 200,
                    'message': 'OK',
                    'xml_content': annotating_xml_content.xml_content,
                }

                response = json.dumps(response)

                # Send message to room group
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'xml_modification',
                        'message': response,
                    }
                )

            except NotModifiedException as exception:
                self.send_response(304, exception)

            except (ValueError, TypeError) as error:
                self.send_response(400, error)

    def send_response(self, code, message):
        response = {
            'status': code,
            'message': str(message),
            'xml_content': None,
        }
        response = json.dumps(response)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'xml_modification',
                'message': response,
            }
        )

    # Receive message from room group
    def xml_modification(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=message)
