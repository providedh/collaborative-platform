import json
import re

from lxml import etree

from apps.close_reading.models import AnnotatingBodyContent
from apps.exceptions import BadRequest
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
        requests = self.__parse_text_data(text_data)

        for request in requests:
            if request['element_type'] == 'tag':
                if request['method'] == 'POST':
                    self.__add_new_tag_to_text(request, user)

                elif request['method'] == 'PUT':
                    self.__move_tag_to_new_position(request, user)

                elif request['method'] == 'DELETE':
                    self.__delete_tag(request, user)

                else:
                    raise BadRequest(f"There is no operation matching to this request")

            pass

    def __add_new_tag_to_text(self, request, user):
        # TODO: Add verification if this same tag not existing already
        # TODO: Add possibility to add tag if text fragment is separated by another tag

        body_content = self.get_body_content()

        max_id = self.__get_max_xml_id_from_text(body_content, 'ab', temp_id=True)
        new_id = max_id + 1

        start_pos = request['start_pos']
        end_pos = request['end_pos']

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

    def __move_tag_to_new_position(self, request, user):
        # TODO: Add verification if user has rights to edit a tag
        # TODO: Add verification if tag wasn't moved by another user in the meantime
        # TODO: Refactor this method to use `__delete_tag()` method

        body_content = self.get_body_content()

        old_start_pos = request['start_pos']
        old_end_pos = request['end_pos']

        new_start_pos = request['parameters']['new_start_pos']
        new_end_pos = request['parameters']['new_end_pos']

        text_before = body_content[:old_start_pos]
        text_inside = body_content[old_start_pos:old_end_pos]
        text_after = body_content[old_end_pos:]

        left_tag_regex = r'<[^<>]+?>\s*$'
        right_tag_regex = r'^\s*</[^<>]+?>'

        match = True

        while match:
            match = re.search(left_tag_regex, text_before)

            if match:
                left_tag_to_move = match.group()

                if request['edited_element_id'] in left_tag_to_move:
                    break

                else:
                    text_before = text_before[:-len(left_tag_to_move)]
                    text_inside = left_tag_to_move + text_inside

                    old_start_pos = old_start_pos - len(left_tag_to_move)

        end_tag_regex = r'^<\w+'
        match = re.search(end_tag_regex, left_tag_to_move)
        close_tag = match.group()
        close_tag = close_tag.replace('<', '</')
        close_tag = close_tag + '>'

        while match:
            match = re.search(right_tag_regex, text_after)

            if match:
                right_tag_to_move = match.group()

                if close_tag in right_tag_to_move:
                    break

                else:
                    text_after = text_after[len(right_tag_to_move):]
                    text_inside = text_inside + right_tag_to_move

                    old_end_pos = old_end_pos + len(right_tag_to_move)

        text_without_tags = text_before[:-len(left_tag_to_move)] + text_inside + text_after[len(right_tag_to_move):]

        if new_start_pos > old_end_pos:
            new_start_pos = new_start_pos - len(left_tag_to_move) - len(right_tag_to_move)
            new_end_pos = new_end_pos + len(left_tag_to_move) - len(right_tag_to_move)
        else:
            if new_start_pos > old_start_pos:
                new_start_pos -= len(left_tag_to_move)
                new_end_pos -= len(right_tag_to_move)

            if new_end_pos > old_end_pos:
                new_end_pos -= len(left_tag_to_move)
                new_end_pos -= len(right_tag_to_move)

        new_text_before = text_without_tags[:new_start_pos]
        new_text_middle = text_without_tags[new_start_pos:new_end_pos]
        new_text_after = text_without_tags[new_end_pos:]

        text_result = new_text_before + left_tag_to_move + new_text_middle + right_tag_to_move + new_text_after

        self.__set_body_content(text_result)

    def __delete_tag(self, request, user):
        # TODO: Add verification if user has rights to delete a tag
        # TODO: Add removing elements connected with deleted tag

        body_content = self.get_body_content()

        tag_xml_id = request['edited_element_id']
        tag_regex_left = f'<[^<>]+xml:id="{tag_xml_id}"[^<>]*>'

        match = re.search(tag_regex_left, body_content)
        tag_left = match.group()

        splitted_text = body_content.split(tag_left)
        text_left = splitted_text[0]
        remaining = splitted_text[1]

        end_tag_regex = r'^<\w+'
        match = re.search(end_tag_regex, tag_left)
        close_tag = match.group()
        close_tag = close_tag.replace('<', '</')
        close_tag = close_tag + '>'

        middle_with_close_tag_regex = f'^[^<>]*{close_tag}'

        match = re.search(middle_with_close_tag_regex, remaining)
        middle_with_close_tag = match.group()

        text_middle = middle_with_close_tag.replace(close_tag, '')
        text_right = remaining.replace(middle_with_close_tag, '')

        text_result = text_left + text_middle + text_right

        self.__set_body_content(text_result)

    @staticmethod
    def __parse_text_data(text_data):
        request = json.loads(text_data)

        return request
