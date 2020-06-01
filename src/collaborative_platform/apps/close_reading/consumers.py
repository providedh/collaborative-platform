import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from django.contrib.auth.models import User

from apps.close_reading.request_handler import RequestHandler
from apps.close_reading.response_generator import ResponseGenerator
from apps.exceptions import BadRequest, Forbidden, NotModified
from apps.files_management.models import File
from apps.projects.models import Contributor, Project

from .models import RoomPresence


logger = logging.getLogger('annotator')


class AnnotatorConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__room_name = ''
        self.__room_group_name = ''

        self.__project_id = ''
        self.__file_id = ''

        self.__file = None

        self.__request_handler = None
        self.__response_generator = None

    def connect(self):
        try:
            self.__room_name = self.scope['url_route']['kwargs']['room_name']
            self.__room_group_name = f'close_reading_{self.__room_name}'
            self.__project_id, self.__file_id = self.__room_name.split('_')

            self.__check_if_project_exist()
            self.__get_file_from_db()
            self.__check_if_user_is_contributor()
            # self.scope['user'] = User.objects.get(id=2)      # For testing

            self.__add_user_to_room_group()
            self.__add_user_to_presence_table()

            self.accept()

            self.__response_generator = ResponseGenerator(self.__file_id)
            self.__request_handler = RequestHandler(self.scope['user'], self.__file_id)

            user_id = self.scope['user'].id
            response = self.__response_generator.get_response(user_id)

            self.send(text_data=response)

        except BadRequest as error:
            self.accept()
            self.__send_error(400, error)
            self.close()

        except Forbidden as error:
            self.accept()
            self.__send_error(403, error)
            self.close()

    def __check_if_project_exist(self):
        try:
            _ = Project.objects.get(id=self.__project_id)
        except Project.DoesNotExist:
            raise BadRequest(f"Project with id: {self.__project_id} doesn't exist.")

    def __get_file_from_db(self):
        try:
            self.__file = File.objects.get(id=self.__file_id, deleted=False)
        except File.DoesNotExist:
            raise BadRequest(f"File with id: {self.__file_id} doesn't exist.")

    def __check_if_user_is_contributor(self):
        contributor = Contributor.objects.filter(project_id=self.__project_id, user_id=self.scope['user'].pk)

        if not contributor:
            raise Forbidden(f"You aren't contributor in project with id: {self.__project_id}.")

    def __add_user_to_room_group(self):
        async_to_sync(self.channel_layer.group_add)(
            self.__room_group_name,
            self.channel_name
        )

        logger.info(f"User: '{self.scope['user'].username}' join to room group: '{self.__room_group_name}'")

    def __add_user_to_presence_table(self):
        room_presence, created = RoomPresence.objects.get_or_create(
            room_symbol=self.__room_name,
            user=self.scope['user'],
            channel_name=self.channel_name,
        )

        room_presence.save()

        logger.info(f"User: '{self.scope['user'].username}' added to 'room_presence' table")

    def disconnect(self, code):
        self.__remove_user_from_room_group()
        self.__remove_user_from_presence_table()

        self.close()

        remain_users = self.__count_remain_users()

        if not remain_users and self.__response_generator:
            self.__response_generator.remove_xml_content()

    def __remove_user_from_room_group(self):
        if self.groups and self.channel_name in self.groups[self.__room_group_name]:
            async_to_sync(self.channel_layer.group_discard)(
                self.__room_group_name,
                self.channel_name
            )

            logger.info(f"User: '{self.scope['user'].username}' left room group: '{self.__room_group_name}'")

    def __remove_user_from_presence_table(self):
        if self.scope['user'].pk is not None:
            room_presences = RoomPresence.objects.filter(
                room_symbol=self.__room_name,
                user=self.scope['user'],
            )

            for presence in room_presences:
                presence.delete()

            logger.info(f"User: '{self.scope['user'].username}' removed from 'room_presence' table")

    def __count_remain_users(self):
        remain_users = RoomPresence.objects.filter(room_symbol=self.__room_name)

        logger.info(f"In room: '{self.__room_name}' left: {len(remain_users)} users")

        return len(remain_users)

    def receive(self, text_data=None, bytes_data=None):
        if text_data == '"heartbeat"':
            self.__update_users_presence()

        elif text_data == 'ping':
            self.send('pong')

        else:
            try:
                # TODO: Add request validator

                logger.info(f"Get request from user: '{self.scope['user'].username}' with content: '{text_data}'")

                request = self.__parse_text_data(text_data)

                if request['method'] == 'modify':
                    operations = request['payload']

                    self.__request_handler.modify_file(operations)
                    self.__send_personalized_changes_to_users()

                elif request['method'] == 'discard':
                    operations_ids = request['payload']

                    self.__request_handler.discard_changes(operations_ids)
                    self.__send_personalized_changes_to_users()

                elif request['method'] == 'save':
                    operations_ids = request['payload']

                    self.__request_handler.save_changes(operations_ids)
                    self.__send_personalized_changes_to_users()

                else:
                    raise BadRequest("There is no operation matching to this request")

            except NotModified as exception:
                self.__send_error(304, exception)

            except BadRequest as error:
                self.__send_error(400, error)

            except Exception:
                self.__send_error(500, "Unhandled exception.")

    def __update_users_presence(self):
        if self.scope['user'].pk is not None:
            room_presences = RoomPresence.objects.filter(
                room_symbol=self.__room_name,
                user=self.scope['user'],
            ).order_by('-timestamp')

            if room_presences:
                room_presence = room_presences[0]
                room_presence.save()

    def __send_personalized_changes_to_users(self):
        room_presences = RoomPresence.objects.filter(
            room_symbol=self.__room_name
        )

        for presence in room_presences:
            user_id = presence.user.id

            response = self.__response_generator.get_response(user_id)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(
                presence.channel_name,
                {
                    'type': 'xml_modification',
                    'message': response,
                }
            )

        user_names = ', '.join([f"'{presence.user.username}'" for presence in room_presences])

        logger.info(f"Content of file: '{self.__file.name}' updated with request from user: "
                    f"'{self.scope['user'].username}' was sent to users: {user_names}")

    def __send_error(self, code, message):
        response = {
            'status': code,
            'message': str(message),
            'body_content': None,
        }

        response = json.dumps(response)
        self.send(text_data=response)

        logger.exception(f"Send response to user: '{self.scope['user'].username}' with content: '{response}'")

    def xml_modification(self, event):
        message = event['message']
        self.send(text_data=message)

    @staticmethod
    def __parse_text_data(text_data):
        request = json.loads(text_data)

        return request
