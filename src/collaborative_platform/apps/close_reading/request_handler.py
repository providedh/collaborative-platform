import json

from lxml import etree

from apps.close_reading.models import AnnotatingBodyContent
from apps.files_management.models import File

from collaborative_platform.settings import XML_NAMESPACES


class RequestHandler:
    def __init__(self, file_id):
        self.__file = None
        self.__body_content = None

        self.__get_file_from_db(file_id)
        self.__load_body_content()

    def __get_file_from_db(self, file_id):
        self.__file = File.objects.get(id=file_id, deleted=False)

    def __load_body_content(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        self.__annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

    def handle_request(self, text_data, user):
        request = self.__parse_text_data(text_data)

        for operation in request:
            if operation['element_type'] == 'tag':
                if operation['method'] == 'POST':
                    self.__add_new_tag_to_text(operation, user)

                elif operation['method'] == 'PUT':
                    pass
                elif operation['method'] == 'DELETE':
                    pass
                else:
                    pass

            pass

    def __add_new_tag_to_text(self, operation, user):
        body_content = self.get_body_content()

        max_id = self.__get_max_xml_id_from_text(body_content, 'ab', temp_id=True)
        new_id = max_id + 1

        start_pos = operation['start_pos']
        end_pos = operation['end_pos']

        text_result = self.__add_tag(body_content, start_pos, end_pos, new_id, user)

        self.__set_body_content(text_result)

    def get_body_content(self):
        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        return body_content

    def __set_body_content(self, body_content):
        self.__annotating_body_content.body_content = body_content
        self.__annotating_body_content.save()

    @staticmethod
    def __add_tag(body_content, start_pos, end_pos, id_nr, user):
        text_before = body_content[:start_pos]
        text_inside = body_content[start_pos:end_pos]
        text_after = body_content[end_pos:]

        text_result = f'{text_before}<ab xml:id="temp_ab-{id_nr}" resp="{user.id}">{text_inside}</ab>{text_after}'

        return text_result

    @staticmethod
    def __get_max_xml_id_from_text(body_content, tag_name, temp_id=False):
        tree = etree.fromstring(body_content)

        if temp_id:
            tag_part = f'temp_{tag_name}-'
        else:
            tag_part = f'{tag_name}-'

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_part}')]/@xml:id"
        elements = tree.xpath(xpath, namespaces=XML_NAMESPACES)

        if elements:
            ids = [int(element.replace(tag_part, '')) for element in elements]
            max_id = max(ids)
        else:
            max_id = 0

        return max_id

    @staticmethod
    def __parse_text_data(text_data):
        request = json.loads(text_data)

        return request
