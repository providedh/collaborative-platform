import json
import re

from lxml import etree

from django.contrib.auth.models import User

from apps.api_vis.models import Entity, EntityProperty, EntityVersion, Certainty
from apps.close_reading.db_handler import DbHandler
from apps.close_reading.enums import TargetTypes
from apps.close_reading.models import AnnotatingBodyContent
from apps.close_reading.response_generator import get_custom_entities_types, get_listable_entities_types, \
    get_unlistable_entities_types
from apps.close_reading.xml_handler import XmlHandler
from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import File, FileMaxXmlIds
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match
from apps.projects.models import UncertaintyCategory

from collaborative_platform.settings import CUSTOM_ENTITY, DEFAULT_ENTITIES, XML_NAMESPACES


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class RequestHandler:
    def __init__(self, user, file_id):
        self.__file = None
        # self.__body_content = None
        #
        self.__get_file_from_db(file_id)
        # self.__load_body_content()

        self.__db_handler = DbHandler(user, file_id)
        self.__xml_handler = XmlHandler(user)

    def __get_file_from_db(self, file_id):
        self.__file = File.objects.get(id=file_id, deleted=False)

    # def __load_body_content(self):
    #     room_name = f'{self.__file.project.id}_{self.__file.id}'
    #
    #     self.__annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

    def handle_request(self, text_data, user):
        requests = self.__parse_text_data(text_data)

        for request in requests:
            if request['element_type'] == 'tag':
                if request['method'] == 'POST':
                    self.__add_new_tag_to_text(request)
                elif request['method'] == 'PUT':
                    self.__move_tag_to_new_position(request, user)
                elif request['method'] == 'DELETE':
                    self.__mark_tag_to_delete(request, user)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'reference':
                if request['method'] == 'POST':
                    self.__add_reference_to_entity(request, user)
                elif request['method'] == 'PUT':
                    self.__modify_reference_to_entity(request, user)
                elif request['method'] == 'DELETE':
                    self.__mark_reference_to_delete(request, user)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'entity_property':
                if request['method'] == 'POST':
                    self.__add_property_to_entity(request, user)
                elif request['method'] == 'PUT':
                    self.__modify_entity_property(request, user)
                elif request['method'] == 'DELETE':
                    self.__mark_property_to_delete(request, user)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'unification':
                raise NotModified("Method not implemented yet")

            elif request['element_type'] == 'certainty':
                if request['method'] == 'POST':
                    self.__add_certainty(request, user)
                elif request['method'] == 'PUT':
                    self.__modify_certainty(request, user)
                elif request['method'] == 'DELETE':
                    self.__mark_certainty_to_delete(request, user)
                else:
                    raise BadRequest("There is no operation matching to this request")

            else:
                raise BadRequest(f"There is no operation matching to this request")

    def __add_new_tag_to_text(self, request):
        # # TODO: Add verification if this same tag not existing already
        # # TODO: Add possibility to add tag if text fragment is separated by another tag
        #
        # body_content = self.get_body_content()
        #
        # xml_id = self.__get_next_xml_id('ab')
        #
        # start_pos = request['parameters']['start_pos']
        # end_pos = request['parameters']['end_pos']
        #
        # text_result = self.__add_tag(body_content, start_pos, end_pos, xml_id, user)
        #
        # self.__set_body_content(text_result)

        xml_id = self.__get_next_xml_id('ab')
        start_pos = request['parameters']['start_pos']
        end_pos = request['parameters']['end_pos']
        body_content = self.__db_handler.get_body_content()

        body_content = self.__xml_handler.add_new_tag_to_text(body_content, xml_id, start_pos, end_pos)

        self.__db_handler.set_body_content(body_content)

    # def get_body_content(self):
    #     self.__annotating_body_content.refresh_from_db()
    #     body_content = self.__annotating_body_content.body_content
    #
    #     return body_content

    # def __set_body_content(self, body_content):
    #     self.__annotating_body_content.body_content = body_content
    #     self.__annotating_body_content.save()

    # @staticmethod
    # def __add_tag(body_content, start_pos, end_pos, xml_id, user):
    #     text_before = body_content[:start_pos]
    #     text_inside = body_content[start_pos:end_pos]
    #     text_after = body_content[end_pos:]
    #
    #     text_result = f'{text_before}<ab xml:id="{xml_id}" resp="#{user.profile.get_xml_id()}" saved="false">{text_inside}</ab>{text_after}'
    #
    #     return text_result

    # @staticmethod
    # def __get_max_xml_id_from_text(body_content, tag_name, temp_id=False):
    #     tree = etree.fromstring(body_content)
    #
    #     if temp_id:
    #         tag_part = f'temp_{tag_name}-'
    #     else:
    #         tag_part = f'{tag_name}-'
    #
    #     xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_part}')]/@xml:id"
    #     elements = tree.xpath(xpath, namespaces=XML_NAMESPACES)
    #
    #     if elements:
    #         ids = [int(element.replace(tag_part, '')) for element in elements]
    #         max_id = max(ids)
    #     else:
    #         max_id = 0
    #
    #     return max_id

    def __move_tag_to_new_position(self, request, user):
        # TODO: Add verification if user has rights to edit a tag
        # TODO: Add verification if tag wasn't moved by another user in the meantime
        # TODO: Refactor this method to use `__delete_tag()` method

        body_content = self.get_body_content()

        edited_element_id = request.get('edited_element_id')
        new_start_pos = request['parameters']['new_start_pos']
        new_end_pos = request['parameters']['new_end_pos']

        temp_xml_id = f'{edited_element_id}-new'

        # Get tag name
        tree = etree.fromstring(body_content)

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {edited_element_id} ')]"
        old_tag_element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        old_tag_name = old_tag_element.tag
        old_tag_name = re.sub(r'{.*?}', '', old_tag_name)

        old_tag_attributes = old_tag_element.attrib

        # Add new tag with temp id
        text_result = self.__add_tag(body_content, new_start_pos, new_end_pos, temp_xml_id, user)

        self.__set_body_content(text_result)

        # Mark old tag to delete
        attributes_to_add = {
            XML_ID_KEY: f'{edited_element_id}-old',
            'deleted': 'true',
            'saved': 'false',
            'resp': f'#{user.profile.get_xml_id()}',
        }

        attributes_to_delete = {
            XML_ID_KEY: edited_element_id,
        }

        self.__update_tag_in_body(edited_element_id, attributes_to_add=attributes_to_add,
                                  attributes_to_delete=attributes_to_delete)

        # update attributes in new tag
        attributes_to_add = {
            XML_ID_KEY: edited_element_id,
            'saved': 'false',
            'resp': f'#{user.profile.get_xml_id()}',
        }

        attributes_to_add = {**old_tag_attributes, **attributes_to_add}

        attributes_to_delete = {
            XML_ID_KEY: temp_xml_id,
        }

        self.__update_tag_in_body(temp_xml_id, new_tag=old_tag_name, attributes_to_add=attributes_to_add,
                                  attributes_to_delete=attributes_to_delete)

    def __mark_tag_to_delete(self, request, user):
        # TODO: Add verification if user has rights to delete a tag

        edited_element_id = request.get('edited_element_id')

        attributes_to_add = {
            'deleted': 'true',
            'saved': 'false',
            'resp': f'#{user.profile.get_xml_id()}',
        }

        self.__update_tag_in_body(edited_element_id, attributes_to_add=attributes_to_add)

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
        new_element_id = request.get('new_element_id')

        try:
            entity_type = request['parameters']['entity_type']
        except KeyError:
            entity_type = Entity.objects.get(xml_id=new_element_id).type


        listable_entities_types = get_listable_entities_types(self.__file.project)

        if not new_element_id and entity_type in listable_entities_types:
            new_element_id = self.__get_next_xml_id(entity_type)
            new_tag_id = self.__get_next_xml_id('name')

            entity_object = self.__create_entity_object(entity_type, new_element_id, user)
            entity_version_object = self.__create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user)

            attributes_to_add = {
                'newId': f'{new_tag_id}',
                'ref': f'#{new_element_id}',
                'unsavedRef': f'#{new_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false',
            }

            self.__update_tag_in_body(edited_element_id, new_tag='name', attributes_to_add=attributes_to_add)

        elif not new_element_id and entity_type not in listable_entities_types:
            new_element_id = self.__get_next_xml_id(entity_type)

            entity_object = self.__create_entity_object(entity_type, new_element_id, user)
            entity_version_object = self.__create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user)

            attributes_to_add = {
                'newId': f'{new_element_id}',
                'ref': f'#{new_element_id}',
                'unsavedRef': f'#{new_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false',
            }

            attributes_to_add.update(entity_properties)

            self.__update_tag_in_body(edited_element_id, new_tag=entity_type, attributes_to_add=attributes_to_add)

        elif new_element_id and entity_type in listable_entities_types:
            new_tag_id = self.__get_next_xml_id('name')

            attributes_to_add = {
                'newId': f'{new_tag_id}',
                'ref': f'#{new_element_id}',
                'unsavedRef': f'#{new_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false',
            }

            self.__update_tag_in_body(edited_element_id, new_tag='name', attributes_to_add=attributes_to_add)

        elif new_element_id and entity_type not in listable_entities_types:
            new_tag_id = self.__get_next_xml_id(entity_type)

            attributes_to_add = {
                'newId': f'{new_tag_id}',
                'ref': f'#{new_element_id}',
                'unsavedRef': f'#{new_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false',
            }

            self.__update_tag_in_body(edited_element_id, new_tag=entity_type, attributes_to_add=attributes_to_add)

        else:
            raise BadRequest("There is no operation matching to this request")

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

    def __update_tag_in_body(self, edited_element_id, new_tag=None, attributes_to_add=None, attributes_to_delete=None):
        body_content = self.get_body_content()
        tree = etree.fromstring(body_content)

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {edited_element_id} ')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if element is None:
            xpath = f"//*[contains(concat(' ', @newId, ' '), ' {edited_element_id} ')]"
            element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if attributes_to_add:
            for attribute, value in sorted(attributes_to_add.items()):
                if new_tag in ['date', 'time'] and attribute == 'name':
                    continue

                if attribute in element.attrib:
                    old_values = element.attrib[attribute]
                    old_values = set(old_values.split(' '))

                    if value not in old_values:
                        old_values.add(value)
                        new_values = ' '.join(sorted(old_values))

                        element.set(attribute, new_values)

                else:
                    element.set(attribute, value)

        if attributes_to_delete:
            for attribute, value in attributes_to_delete.items():
                if attribute in element.attrib:
                    old_values = element.attrib[attribute]
                    old_values = set(old_values.split(' '))

                    if value in old_values:
                        old_values.remove(value)

                    if old_values:
                        new_values = ' '.join(sorted(old_values))
                        element.attrib[attribute] = new_values
                    else:
                        element.attrib.pop(attribute)

        references = element.attrib.get('ref')

        if references:
            references = set(references.split(' '))
        else:
            references = set()

        references_deleted = element.attrib.get('refDeleted')

        if references_deleted:
            references_deleted = set(references_deleted.split(' '))
        else:
            references_deleted = set()

        remaining_references = references - references_deleted

        if not remaining_references:
            tag_name = element.tag
            tag_name = re.sub(r'{.*?}', '', tag_name)

            unlistable_entities_types = get_unlistable_entities_types(self.__file.project)

            if tag_name in unlistable_entities_types:
                xml_id = element.attrib[XML_ID_KEY]

                entity_version = EntityVersion.objects.filter(
                    file_version=self.__file.file_versions.order_by('-id')[0],
                    entity__xml_id=xml_id
                )

                if not entity_version:
                    prefix = "{%s}" % XML_NAMESPACES['default']
                    tag = prefix + 'ab'
                    element.tag = tag

                elif f'#{xml_id}' in references_deleted:
                    prefix = "{%s}" % XML_NAMESPACES['default']
                    tag = prefix + 'ab'
                    element.tag = tag

            else:
                prefix = "{%s}" % XML_NAMESPACES['default']
                tag = prefix + 'ab'
                element.tag = tag

        if new_tag:
            prefix = "{%s}" % XML_NAMESPACES['default']
            tag = prefix + new_tag
            element.tag = tag

        text_result = etree.tounicode(tree, pretty_print=True)

        self.__set_body_content(text_result)

    def __modify_reference_to_entity(self, request, user):
        # TODO: Add verification if user has rights to edit a tag

        edited_element_id = request.get('edited_element_id')
        old_element_id = request.get('old_element_id')
        new_element_id = request.get('new_element_id')

        try:
            entity_type = request['parameters']['entity_type']
        except KeyError:
            entity_type = Entity.objects.get(xml_id=old_element_id).type

        listable_entities_types = get_listable_entities_types(self.__file.project)

        if not new_element_id and entity_type in listable_entities_types:
            new_element_id = self.__get_next_xml_id(entity_type)

            entity_object = self.__create_entity_object(entity_type, new_element_id, user)
            entity_version_object = self.__create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user)

            attributes_to_add = {
                'ref': f'#{new_element_id}',
                'refAdded': f'#{new_element_id}',
                'refDeleted': f'#{old_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false'
            }

            edited_element_id_base = edited_element_id.split('-')[0]

            if edited_element_id_base != 'name':
                new_tag_id = self.__get_next_xml_id('name')

                attributes_to_add.update({'newId': f'{new_tag_id}'})

            self.__update_tag_in_body(edited_element_id, new_tag='name', attributes_to_add=attributes_to_add)

            last_reference = self.__check_if_last_reference(old_element_id)

            if last_reference:
                self.__mark_entities_to_delete(old_element_id, user)

        elif not new_element_id and entity_type not in listable_entities_types:
            new_element_id = self.__get_next_xml_id(entity_type)

            entity_object = self.__create_entity_object(entity_type, new_element_id, user)
            entity_version_object = self.__create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__create_entity_properties_objects(entity_type, entity_properties, entity_version_object, user)

            attributes_to_add = {
                'ref': f'#{new_element_id}',
                'refAdded': f'#{new_element_id}',
                'refDeleted': f'#{old_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false'
            }

            edited_element_id_base = edited_element_id.split('-')[0]

            if edited_element_id_base != entity_type:
                new_tag_id = self.__get_next_xml_id(entity_type)

                attributes_to_add.update({'newId': f'{new_tag_id}'})

            for name, value in entity_properties.items():
                if name == 'name':
                    continue

                attributes_to_add.update({name: value})

            self.__update_tag_in_body(edited_element_id, new_tag=entity_type, attributes_to_add=attributes_to_add)

            last_reference = self.__check_if_last_reference(old_element_id)

            if last_reference:
                self.__mark_entities_to_delete(old_element_id, user)

        elif new_element_id and entity_type in listable_entities_types:
            attributes_to_add = {
                'ref': f'#{new_element_id}',
                'refAdded': f'#{new_element_id}',
                'refDeleted': f'#{old_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false'
            }

            edited_element_id_base = edited_element_id.split('-')[0]

            if edited_element_id_base != 'name':
                new_tag_id = self.__get_next_xml_id('name')

                attributes_to_add.update({'newId': f'{new_tag_id}'})

            self.__update_tag_in_body(edited_element_id, new_tag='name', attributes_to_add=attributes_to_add)

            last_reference = self.__check_if_last_reference(old_element_id)

            if last_reference:
                self.__mark_entities_to_delete(old_element_id, user)

        elif new_element_id and entity_type not in listable_entities_types:
            attributes_to_add = {
                'ref': f'#{new_element_id}',
                'refAdded': f'#{new_element_id}',
                'refDeleted': f'#{old_element_id}',
                'resp': f'#{user.profile.get_xml_id()}',
                'saved': 'false'
            }

            edited_element_id_base = edited_element_id.split('-')[0]

            if edited_element_id_base != entity_type:
                new_tag_id = self.__get_next_xml_id(entity_type)

                attributes_to_add.update({'newId': f'{new_tag_id}'})

            self.__update_tag_in_body(edited_element_id, new_tag=entity_type, attributes_to_add=attributes_to_add)

            last_reference = self.__check_if_last_reference(old_element_id)

            if last_reference:
                self.__mark_entities_to_delete(old_element_id, user)

        else:
            raise BadRequest("There is no operation matching to this request")

    def __check_if_last_reference(self, target_element_id):
        body_content = self.get_body_content()
        tree = etree.fromstring(body_content)

        xpath = f"//*[contains(concat(' ', @ref, ' '), ' {target_element_id} ')]"
        all_references = tree.xpath(xpath, namespaces=XML_NAMESPACES)

        if len(all_references) > 1:
            return False
        else:
            return True

    def __mark_entities_to_delete(self, target_element_id, user):
        entity = Entity.objects.get(xml_id=target_element_id)
        entity.deleted_by = user
        entity.save()

        entity_properties = EntityProperty.objects.filter(
            entity_version=entity.entityversion_set.all().order_by('-id')[0]
        )

        for entity_property in entity_properties:
            entity_property.deleted_by = user

        EntityProperty.objects.bulk_update(entity_properties, ['deleted_by'])

        certainties = Certainty.objects.filter(
            file_version=self.__file.file_versions.order_by('-number')[0],
            target_xml_id=target_element_id
        )

        # TODO: Add marking certainties to properties to delete

        for certainty in certainties:
            certainty.deleted_by = user

        Certainty.objects.bulk_update(certainties, ['deleted_by'])

    def __mark_reference_to_delete(self, request, user):
        # TODO: add attribute `newId="ab-XX"`, when tag name will be changed to 'ab'

        edited_element_id = request.get('edited_element_id')
        old_element_id = request.get('old_element_id')

        attributes_to_add = {
            'refDeleted': f'#{old_element_id}',
            'saved': 'false',
            'resp': f'#{user.profile.get_xml_id()}',
        }

        self.__update_tag_in_body(edited_element_id, attributes_to_add=attributes_to_add)

        last_reference = self.__check_if_last_reference(old_element_id)

        if last_reference:
            self.__mark_entities_to_delete(old_element_id, user)

    def __get_next_xml_id(self, entity_type):
        entity_max_xml_id = FileMaxXmlIds.objects.get(
            file=self.__file,
            xml_id_base=entity_type,
        )

        xml_id_nr = entity_max_xml_id.get_next_number()
        xml_id = f'{entity_type}-{xml_id_nr}'

        return xml_id

    def __add_property_to_entity(self, request, user):
        edited_element_id = request.get('edited_element_id')
        entity_type = Entity.objects.get(xml_id=edited_element_id).type

        listable_entities_types = get_listable_entities_types(self.__file.project)

        if entity_type in listable_entities_types:
            entity_property = request['parameters']

            entity_version_objects = EntityVersion.objects.filter(
                entity__xml_id=edited_element_id,
                file_version__isnull=False
            ).order_by('-file_version')

            if not entity_version_objects:
                entity_version_objects = EntityVersion.objects.filter(
                    entity__xml_id=edited_element_id,
                    file_version__isnull=True
                ).order_by('-id')

            entity_version_object = entity_version_objects[0]

            self.__create_entity_properties_objects(entity_type, entity_property, entity_version_object, user)

        else:
            entity_property = request['parameters']

            entity_version_objects = EntityVersion.objects.filter(
                entity__xml_id=edited_element_id,
                file_version__isnull=False
            ).order_by('-file_version')

            if not entity_version_objects:
                entity_version_objects = EntityVersion.objects.filter(
                    entity__xml_id=edited_element_id,
                    file_version__isnull=True
                ).order_by('-id')

            entity_version_object = entity_version_objects[0]

            attributes_to_add = {f'{key}Added': value for key, value in entity_property.items()}
            attributes_to_add.update({'saved': 'false'})

            self.__create_entity_properties_objects(entity_type, entity_property, entity_version_object, user)

            self.__update_tag_in_body(edited_element_id, attributes_to_add=attributes_to_add)

    def __mark_property_to_delete(self, request, user):
        edited_element_id = request.get('edited_element_id')
        entity_type = Entity.objects.get(xml_id=edited_element_id).type

        listable_entities_types = get_listable_entities_types(self.__file.project)

        if entity_type in listable_entities_types:
            property_to_delete = request['old_element_id']

            entity_property = EntityProperty.objects.filter(
                entity_version__entity__xml_id=edited_element_id,
                name=property_to_delete,
            ).order_by('-id')[0]

            entity_property.deleted_by = user
            entity_property.save()

        else:
            property_to_delete = request['old_element_id']

            entity_property = EntityProperty.objects.filter(
                entity_version__entity__xml_id=edited_element_id,
                name=property_to_delete,
            ).order_by('-id')[0]

            entity_property.deleted_by = user
            entity_property.save()

            property_value = entity_property.get_value(as_str=True)

            attributes_to_add = {
                f'{property_to_delete}Deleted': property_value
            }

            attributes_to_delete = {
                property_to_delete: property_value
            }

            self.__update_tag_in_body(edited_element_id, attributes_to_add=attributes_to_add,
                                      attributes_to_delete=attributes_to_delete)

    def __modify_entity_property(self, request, user):
        edited_element_id = request.get('edited_element_id')
        entity_type = Entity.objects.get(xml_id=edited_element_id).type

        listable_entities_types = get_listable_entities_types(self.__file.project)

        if entity_type in listable_entities_types:
            property_to_delete = request['old_element_id']

            entity_property = EntityProperty.objects.filter(
                entity_version__entity__xml_id=edited_element_id,
                name=property_to_delete,
            ).order_by('-id')[0]

            entity_property.deleted_by = user
            entity_property.save()

            entity_property = request['parameters']

            entity_version_objects = EntityVersion.objects.filter(
                entity__xml_id=edited_element_id,
                file_version__isnull=False
            ).order_by('-file_version')

            if not entity_version_objects:
                entity_version_objects = EntityVersion.objects.filter(
                    entity__xml_id=edited_element_id,
                    file_version__isnull=True
                ).order_by('-id')

            entity_version_object = entity_version_objects[0]

            self.__create_entity_properties_objects(entity_type, entity_property, entity_version_object, user)

        else:
            property_to_delete = request['old_element_id']

            entity_property_object = EntityProperty.objects.filter(
                entity_version__entity__xml_id=edited_element_id,
                name=property_to_delete,
            ).order_by('-id')[0]

            entity_property_object.deleted_by = user
            entity_property_object.save()

            entity_property = request['parameters']

            entity_version_objects = EntityVersion.objects.filter(
                entity__xml_id=edited_element_id,
                file_version__isnull=False
            ).order_by('-file_version')

            if not entity_version_objects:
                entity_version_objects = EntityVersion.objects.filter(
                    entity__xml_id=edited_element_id,
                    file_version__isnull=True
                ).order_by('-id')

            entity_version_object = entity_version_objects[0]

            self.__create_entity_properties_objects(entity_type, entity_property, entity_version_object, user)

            property_value = entity_property_object.get_value(as_str=True)

            attributes_to_add = {f'{key}Added': value for key, value in entity_property.items()}

            attributes_to_add_extension = {
                f'{property_to_delete}Deleted': property_value,
                'saved': 'false'
            }

            attributes_to_add = {**attributes_to_add, **attributes_to_add_extension}

            self.__update_tag_in_body(edited_element_id, attributes_to_add=attributes_to_add)

    def __add_certainty(self, request, user):
        certainty_target = request['new_element_id']
        locus = request['parameters']['locus']

        target_type = self.get_certainty_target_type(certainty_target, locus)
        target, match = self.get_certainty_target_and_match(certainty_target, target_type)

        # Create certainty object

        xml_id = self.__get_next_xml_id('certainty')

        certainty_object = Certainty.objects.create(
            file=self.__file,
            xml_id=xml_id,
            locus=request['parameters'].get('locus'),
            cert=request['parameters'].get('certainty'),
            target_xml_id=target,
            target_match=match,
            asserted_value=request['parameters'].get('asserted_value'),
            description=request['parameters'].get('description'),
            created_by=user
        )

        categories = request['parameters'].get('categories')
        categories_ids = self.__get_categories_ids_from_db(categories)

        certainty_object.categories.add(*categories_ids)

    @staticmethod
    def get_certainty_target_type(certainty_target, locus):
        if 'certainty-' in certainty_target:
            target_type = TargetTypes.certainty
        elif '/' in certainty_target:
            target_type = TargetTypes.entity_property
        elif '@ref' in certainty_target:
            target_type = TargetTypes.reference
        elif locus == 'value':
            target_type = TargetTypes.text
        elif locus == 'name':
            target_type = TargetTypes.entity_type
        else:
            raise BadRequest("There is no operation matching to this request")

        return target_type

    def get_certainty_target_and_match(self, certainty_target, target_type):
        if target_type == TargetTypes.text:
            target_xml_id = certainty_target
            target_match = None

        elif target_type == TargetTypes.reference:
            target_xml_id = certainty_target.split('@')[0]
            target_match = '@ref'

        elif target_type == TargetTypes.entity_type:
            custom_entities_types = get_custom_entities_types(self.__file.project)

            entity = Entity.objects.get(
                xml_id=certainty_target,
                file=self.__file
            )

            if entity.type not in custom_entities_types:
                target_xml_id = certainty_target
                target_match = None
            else:
                target_xml_id = certainty_target
                target_match = '@type'

        elif target_type == TargetTypes.entity_property:
            target_xml_id = certainty_target.split('/')[0]
            property_name = certainty_target.split('/')[1]

            property = EntityProperty.objects.get(
                entity_version__entity__xml_id=target_xml_id,
                name=property_name,
                entity_version__file_version=self.__file.file_versions.order_by('-number')[0]
            )

            target_match = property.xpath

        elif target_type == TargetTypes.certainty:
            target_xml_id = certainty_target
            target_match = None

        else:
            raise BadRequest("There is no operation matching to this request")

        return target_xml_id, target_match




    def __get_categories_ids_from_db(self, categories):
        categories = UncertaintyCategory.objects.filter(
            taxonomy__project=self.__file.project,
            name__in=categories
        )

        categories_ids = categories.values_list('id', flat=True)

        return categories_ids

    def __mark_certainty_to_delete(self, request, user):
        certainty_id = request['edited_element_id']

        certainty = Certainty.objects.get(
            xml_id=certainty_id,
            file_version=self.__file.file_versions.order_by('-number')[0]
        )

        certainty.deleted_by = user
        certainty.save()

    def __modify_certainty(self, request, user):
        certainty_id = request['edited_element_id']

        try:
            certainty = Certainty.objects.get(
                xml_id=certainty_id,
                file=self.__file,
                file_version__isnull=True
            )
        except Certainty.DoesNotExist:
            certainty = Certainty.objects.get(
                xml_id=certainty_id,
                file_version=self.__file.file_versions.order_by('-number')[0]
            )

            certainty.deleted_by = user
            certainty.save()

            certainty_categories = certainty.categories.all()

            certainty.id = None
            certainty.created_in_file_version = None
            certainty.deleted_by = None
            certainty.file_version = None
            certainty.save()

            for category in certainty_categories:
                certainty.categories.add(category)

        parameter_name = request['old_element_id']

        if parameter_name == 'categories':
            categories = certainty.categories.all()

            for category in categories:
                certainty.categories.remove(category)

            categories = request['parameters'].get('categories')
            categories_ids = self.__get_categories_ids_from_db(categories)

            certainty.categories.add(*categories_ids)

        elif parameter_name == 'locus':
            locus = request['parameters'].get('locus')
            certainty.locus = locus
            certainty.save()

        elif parameter_name == 'certainty':
            cert = request['parameters'].get('certainty')
            certainty.cert = cert
            certainty.save()

        elif parameter_name == 'asserted_value':
            asserted_value = request['parameters'].get('asserted_value')
            certainty.asserted_value = asserted_value
            certainty.save()

        elif parameter_name == 'description':
            description = request['parameters'].get('description')
            certainty.description = description
            certainty.save()

        elif parameter_name == 'reference':
            certainty_target = request['parameters']['new_element_id']
            locus = request['parameters']['locus']

            target_type = self.get_certainty_target_type(certainty_target, locus)
            target, match = self.get_certainty_target_and_match(certainty_target, target_type)

            certainty.target_xml_id = target
            certainty.target_match = match
            certainty.save()

        else:
            raise BadRequest("There is no operation matching to this request")
