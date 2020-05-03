import json
import re

from lxml import etree

from django.contrib.auth.models import User

from apps.api_vis.models import Entity, EntityProperty, EntityVersion
from apps.close_reading.models import AnnotatingBodyContent
from apps.exceptions import BadRequest
from apps.files_management.models import File, FileMaxXmlIds
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match
from apps.close_reading.response_generator import get_entities_types_for_lists

from collaborative_platform.settings import CUSTOM_ENTITY, DEFAULT_ENTITIES, XML_NAMESPACES


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
                    self.__mark_tag_to_delete(request, user)
                else:
                    raise BadRequest(f"There is no operation matching to this request")

            elif request['element_type'] == 'reference':
                if request['method'] == 'POST':
                    self.__add_reference_to_entity(request, user)
                elif request['method'] == 'PUT':
                    pass
                elif request['method'] == 'DELETE':
                    self.__mark_reference_to_delete(request, user)
                else:
                    raise BadRequest(f"There is no operation matching to this request")

            else:
                raise BadRequest(f"There is no operation matching to this request")


            pass

    def __add_new_tag_to_text(self, request, user):
        # TODO: Add verification if this same tag not existing already
        # TODO: Add possibility to add tag if text fragment is separated by another tag

        body_content = self.get_body_content()

        xml_id = self.__get_next_xml_id('ab')

        start_pos = request['start_pos']
        end_pos = request['end_pos']

        text_result = self.__add_tag(body_content, start_pos, end_pos, xml_id, user)

        self.__set_body_content(text_result)

    def get_body_content(self):
        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        return body_content

    def __set_body_content(self, body_content):
        self.__annotating_body_content.body_content = body_content
        self.__annotating_body_content.save()

    @staticmethod
    def __add_tag(body_content, start_pos, end_pos, xml_id, user):
        text_before = body_content[:start_pos]
        text_inside = body_content[start_pos:end_pos]
        text_after = body_content[end_pos:]

        text_result = f'{text_before}<ab xml:id="{xml_id}" resp="{user.username}" saved="false">{text_inside}</ab>{text_after}'

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

    def __mark_tag_to_delete(self, request, user):
        # TODO: Add verification if user has rights to delete a tag

        edited_xml_id = request.get('edited_element_id')

        tree = etree.fromstring(self.get_body_content())

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {edited_xml_id}')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        element.set('deleted', 'true')

        text_result = etree.tounicode(tree, pretty_print=True)

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

    def __add_reference_to_entity(self, request, user):  # type: (dict, User) -> None
        # TODO: Add verification if user has rights to edit a tag

        edited_element_id = request.get('edited_element_id')
        target_element_id = request.get('target_element_id')

        try:
            entity_type = request['parameters']['entity_type']
        except KeyError:
            entity_type = Entity.objects.get(xml_id=target_element_id).type


        listable_entities_types = get_entities_types_for_lists(self.__file.project)

        if not target_element_id and entity_type in listable_entities_types:
            target_element_id = self.__get_next_xml_id(entity_type)

            entity_object = self.__create_entity_object(entity_type, target_element_id, user)
            entity_version_object = self.__create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user)

            attributes_to_set = {
                'ref': f'#{target_element_id}',
                'unsavedRef': f'#{target_element_id}'
            }

            self.__update_tag_in_body(edited_element_id, new_tag='name', attributes_to_set=attributes_to_set)

        elif not target_element_id and entity_type not in listable_entities_types:
            target_element_id = self.__get_next_xml_id(entity_type)

            entity_object = self.__create_entity_object(entity_type, target_element_id, user)
            entity_version_object = self.__create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user)

            attributes_to_set = {
                'saved': 'false'
            }

            attributes_to_set.update(entity_properties)

            self.__update_tag_in_body(edited_element_id, new_tag=entity_type, attributes_to_set=attributes_to_set)

        elif target_element_id and entity_type in listable_entities_types:
            attributes_to_set = {
                'ref': f'#{target_element_id}',
                'unsavedRef': f'#{target_element_id}'
            }

            self.__update_tag_in_body(edited_element_id, new_tag='name', attributes_to_set=attributes_to_set)

        elif target_element_id and entity_type not in listable_entities_types:
            attributes_to_set = {
                'ref': f'#{target_element_id}',
                'unsavedRef': f'#{target_element_id}'
            }

            self.__update_tag_in_body(edited_element_id, new_tag=entity_type, attributes_to_set=attributes_to_set)

        else:
            raise BadRequest(f"There is no operation matching to this request")

    def __create_entity_object(self, entity_type, xml_id, user):
        entity_object = Entity.objects.create(
            file=self.__file,
            type=entity_type,
            xml_id=xml_id,
            created_by=user,
        )

        return entity_object

    @staticmethod
    def __create_entity_version_object(entity_object):
        entity_version_object = EntityVersion.objects.create(
            entity=entity_object,
        )

        return entity_version_object

    @staticmethod
    def __create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user):
        if entity_type in DEFAULT_ENTITIES.keys():
            properties = DEFAULT_ENTITIES[entity_type]['properties']
        else:
            properties = CUSTOM_ENTITY['properties']

        properties_objects = []

        for name, value in entity_properties.items():
            entity_property_object = EntityProperty(
                entity_version=entity_version_object,
                xpath='',
                name=name,
                type=properties[name]['type'],
                created_by=user,
            )

            entity_property_object.set_value(value)

            properties_objects.append(entity_property_object)

        EntityProperty.objects.bulk_create(properties_objects)

    def __update_tag_in_body(self, edited_element_id, new_tag=None, attributes_to_set=None, attributes_to_delete=None):
        body_content = self.get_body_content()
        tree = etree.fromstring(body_content)

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {edited_element_id}')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if new_tag:
            prefix = "{%s}" % XML_NAMESPACES['default']
            tag = prefix + new_tag
            element.tag = tag

        if attributes_to_set:
            for attribute, value in sorted(attributes_to_set.items()):
                if attribute in element.attrib:
                    old_value = element.attrib[attribute]

                    if value not in old_value:
                        value = ' '.join((old_value, value))

                element.set(attribute, value)

        if attributes_to_delete:
            for attribute in attributes_to_delete:
                element.attrib.pop(attribute)

        text_result = etree.tounicode(tree, pretty_print=True)

        self.__set_body_content(text_result)

    def __mark_reference_to_delete(self, request, user):
        # update tag

        edited_element_id = request.get('edited_element_id')
        target_element_id = request.get('target_element_id')

        body_content = self.get_body_content()
        tree = etree.fromstring(body_content)

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {edited_element_id}')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        element.set('deletedRef', f'#{target_element_id}')

        if edited_element_id != target_element_id:
            ids_in_ref = element.attrib['ref']
            ids_in_ref = ids_in_ref.split(' ')

            ids_in_deleted_ref = element.attrib['deletedRef']
            ids_in_deleted_ref = ids_in_deleted_ref.split(' ')

            remaining_ids = set(ids_in_ref) - set(ids_in_deleted_ref)
        else:
            remaining_ids = {}

        if not remaining_ids:
            prefix = "{%s}" % XML_NAMESPACES['default']
            tag = prefix + 'ab'
            element.tag = tag

            element.set('saved', 'false')


        # update objects

        xpath = f"//*[contains(concat(' ', @ref, ' '), ' #{target_element_id} ')]"
        all_references = tree.xpath(xpath, namespaces=XML_NAMESPACES)

        remaining_references = set(all_references) - {element}

        if not remaining_references:
            entity = Entity.objects.get(xml_id=target_element_id)
            entity.deleted_by = user
            entity.save()

            entity_properties = EntityProperty.objects.filter(
                entity_version=entity.entityversion_set.all().order_by('-id')[0]
            )

            for entity_property in entity_properties:
                entity_property.deleted_by = user

            EntityProperty.objects.bulk_update(entity_properties, ['deleted_by'])

        text_result = etree.tounicode(tree, pretty_print=True)

        self.__set_body_content(text_result)











    def __get_next_xml_id(self, entity_type):
        entity_max_xml_id = FileMaxXmlIds.objects.get(
            file=self.__file,
            xml_id_base=entity_type,
        )

        xml_id_nr = entity_max_xml_id.get_next_number()
        xml_id = f'{entity_type}-{xml_id_nr}'

        return xml_id

