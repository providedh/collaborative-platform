import json

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer

from apps.exceptions import BadRequest, Forbidden
from apps.files_management.models import File
from apps.projects.models import Contributor, Project


class PoetryConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__room_name = ''

        self.__project_id = ''
        self.__file_id = ''

        self.__file = None

        self.__request_handler = None
        self.__response_generator = None

    def connect(self):
        try:
            self.__room_name = self.scope['url_route']['kwargs']['room_name']
            self.__project_id, self.__file_id = self.__room_name.split('_')

            self.__check_if_project_exist()
            self.__get_file_from_db()
            self.__check_if_user_is_contributor()
            # self.scope['user'] = User.objects.get(id=2)      # For manual testing

            self.accept()

            self.__file = File.objects.get(id=self.__file_id, deleted=False)
            file_content = self.__file.get_rendered_content()

            response = {
                'status': 200,
                'message': 'OK',
                'file_content': file_content
            }

            response = json.dumps(response)

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
        contributor = Contributor.objects.filter(project_id=self.__project_id, user_id=self.scope['user'].id)

        if not contributor:
            raise Forbidden(f"You aren't contributor in project with id: {self.__project_id}.")

    def disconnect(self, code):
        self.close()

        raise StopConsumer()

    def receive(self, text_data=None, bytes_data=None):
        self.send(f'Message from backend: {text_data}')

    def __send_error(self, code, message):
        response = {
            'status': code,
            'message': str(message),
            'body_content': None,
        }

        response = json.dumps(response)
        self.send(text_data=response)

    def xml_modification(self, event):
        message = event['message']
        self.send(text_data=message)
