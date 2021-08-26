import json
import re

from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from lxml import etree
from rantanplan.core import get_scansion

from apps.exceptions import BadRequest, Forbidden
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match
from apps.files_management.models import File
from apps.projects.models import Contributor, Project

from collaborative_platform.settings import XML_NAMESPACES


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

            file_content = self.__file.get_rendered_content()
            body_content = self.__get_body_content(file_content)

            tag_regex = r'<.*?>'
            clean_text = re.sub(tag_regex, '', body_content)

            leading_spaces_regex = r'^[ ]+'
            clean_text = re.sub(leading_spaces_regex, '', clean_text, flags=re.MULTILINE)

            multiple_line_breaks_regex = r'[\n]{2,}'
            clean_text = re.sub(multiple_line_breaks_regex, '\n\n', clean_text)

            line_breaks_on_beginning_regex = r'^[\n]+'
            clean_text = re.sub(line_breaks_on_beginning_regex, '', clean_text)

            line_breaks_on_end_regex = r'[\n]+$'
            clean_text = re.sub(line_breaks_on_end_regex, '', clean_text)

            scansion = get_scansion(clean_text)

            response = {
                'status': 200,
                'message': 'OK',
                'file_content': file_content,
                'scansion': scansion,
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

    @staticmethod
    def __get_body_content(xml_content):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(xml_content, parser=parser)

        body_xpath = './default:text'
        body_element = get_first_xpath_match(tree, body_xpath, XML_NAMESPACES)

        body_content = etree.tounicode(body_element, pretty_print=True)

        return body_content

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
