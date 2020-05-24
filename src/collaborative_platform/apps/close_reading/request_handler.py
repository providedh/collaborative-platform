import json

from apps.api_vis.models import Entity
from apps.close_reading.db_handler import DbHandler
from apps.close_reading.response_generator import get_custom_entities_types, get_listable_entities_types, \
    get_unlistable_entities_types
from apps.close_reading.xml_handler import XmlHandler
from apps.exceptions import BadRequest, NotModified


class RequestHandler:
    def __init__(self, user, file_id):
        self.__db_handler = DbHandler(user, file_id)
        self.__file = self.__db_handler.get_file_from_db(file_id)
        self.__annotator_xml_id = self.__db_handler.get_annotator_xml_id()

        self.__listable_entities_types = get_listable_entities_types(self.__file.project)
        self.__custom_entities_types = get_custom_entities_types(self.__file.project)

        unlistable_entities_types = get_unlistable_entities_types(self.__file.project)

        self.__xml_handler = XmlHandler(self.__listable_entities_types, unlistable_entities_types,
                                        self.__custom_entities_types, self.__annotator_xml_id)

    def handle_request(self, text_data):
        requests = self.__parse_text_data(text_data)

        for request in requests:
            if request['element_type'] == 'tag':
                if request['method'] == 'POST':
                    self.__add_tag(request)
                elif request['method'] == 'PUT':
                    self.__move_tag(request)
                elif request['method'] == 'DELETE':
                    self.__delete_tag(request)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'reference':
                if request['method'] == 'POST':
                    self.__add_reference_to_entity(request)
                elif request['method'] == 'PUT':
                    self.__modify_reference_to_entity(request)
                elif request['method'] == 'DELETE':
                    self.__delete_reference_to_entity(request)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'entity_property':
                if request['method'] == 'POST':
                    self.__add_entity_property(request)
                elif request['method'] == 'PUT':
                    self.__modify_entity_property(request)
                elif request['method'] == 'DELETE':
                    self.__delete_entity_property(request)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'unification':
                raise NotModified("Method not implemented yet")

            elif request['element_type'] == 'certainty':
                if request['method'] == 'POST':
                    self.__add_certainty(request)
                elif request['method'] == 'PUT':
                    self.__modify_certainty(request)
                elif request['method'] == 'DELETE':
                    self.__delete_certainty(request)
                else:
                    raise BadRequest("There is no operation matching to this request")

            else:
                raise BadRequest(f"There is no operation matching to this request")

    @staticmethod
    def __parse_text_data(text_data):
        request = json.loads(text_data)

        return request

    def __add_tag(self, request):
        # TODO: Add verification if this same tag not existing already
        # TODO: Add possibility to add tag if text fragment is separated by another tag

        body_content = self.__db_handler.get_body_content()
        start_pos = request['parameters']['start_pos']
        end_pos = request['parameters']['end_pos']
        tag_xml_id = self.__db_handler.get_next_xml_id('ab')

        body_content = self.__xml_handler.add_new_tag_to_text(body_content, start_pos, end_pos, tag_xml_id,
                                                              self.__annotator_xml_id)

        self.__db_handler.set_body_content(body_content)

    def __move_tag(self, request):
        # TODO: Add verification if user has rights to edit a tag
        # TODO: Add verification if tag wasn't moved by another user in the meantime

        body_content = self.__db_handler.get_body_content()
        new_start_pos = request['parameters']['new_start_pos']
        new_end_pos = request['parameters']['new_end_pos']
        tag_xml_id = request.get('edited_element_id')

        body_content = self.__xml_handler.move_tag_to_new_position(body_content, new_start_pos, new_end_pos, tag_xml_id,
                                                                   self.__annotator_xml_id)

        self.__db_handler.set_body_content(body_content)

    def __delete_tag(self, request):
        # TODO: Add verification if user has rights to delete a tag

        body_content = self.__db_handler.get_body_content()
        tag_xml_id = request.get('edited_element_id')

        body_content = self.__xml_handler.mark_tag_to_delete(body_content, tag_xml_id, self.__annotator_xml_id)

        self.__db_handler.set_body_content(body_content)

    def __add_reference_to_entity(self, request):
        # TODO: Add verification if user has rights to edit a tag

        tag_xml_id = request.get('edited_element_id')
        entity_xml_id = request.get('new_element_id')

        try:
            entity_type = request['parameters']['entity_type']
        except KeyError:
            entity_type = Entity.objects.get(xml_id=entity_xml_id).type

        if not entity_xml_id and entity_type in self.__listable_entities_types:
            new_tag = 'name'
            entity_xml_id = self.__db_handler.get_next_xml_id(entity_type)
            new_tag_xml_id = self.__db_handler.get_next_xml_id(new_tag)

            entity_object = self.__db_handler.create_entity_object(entity_type, entity_xml_id)
            entity_version_object = self.__db_handler.create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__db_handler.create_entity_properties_objects(entity_type, entity_properties, entity_version_object)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, new_tag, new_tag_xml_id,
                                                                      entity_xml_id, self.__annotator_xml_id)

            self.__db_handler.set_body_content(body_content)

        elif not entity_xml_id and entity_type not in self.__listable_entities_types:
            entity_xml_id = self.__db_handler.get_next_xml_id(entity_type)

            entity_object = self.__db_handler.create_entity_object(entity_type, entity_xml_id)
            entity_version_object = self.__db_handler.create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__db_handler.create_entity_properties_objects(entity_type, entity_properties, entity_version_object)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, entity_type,
                                                                      entity_xml_id, entity_xml_id,
                                                                      self.__annotator_xml_id)

            entity_properties.pop('name', '')

            body_content = self.__xml_handler.add_properties_to_tag(body_content, entity_xml_id, entity_properties)

            self.__db_handler.set_body_content(body_content)

        elif entity_xml_id and entity_type in self.__listable_entities_types:
            new_tag = 'name'
            new_tag_xml_id = self.__db_handler.get_next_xml_id(new_tag)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, new_tag, new_tag_xml_id,
                                                                      entity_xml_id, self.__annotator_xml_id)

            self.__db_handler.set_body_content(body_content)

        elif entity_xml_id and entity_type not in self.__listable_entities_types:
            new_tag_xml_id = self.__db_handler.get_next_xml_id(entity_type)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, entity_type,
                                                                      new_tag_xml_id, entity_xml_id,
                                                                      self.__annotator_xml_id)

            self.__db_handler.set_body_content(body_content)

        else:
            raise BadRequest("There is no operation matching to this request")

    def __modify_reference_to_entity(self, request):
        # TODO: Add verification if user has rights to edit a tag

        tag_xml_id = request.get('edited_element_id')
        old_entity_xml_id = request.get('old_element_id')
        new_entity_xml_id = request.get('new_element_id')

        try:
            entity_type = request['parameters']['entity_type']
        except KeyError:
            entity_type = Entity.objects.get(xml_id=old_entity_xml_id).type

        if not new_entity_xml_id and entity_type in self.__listable_entities_types:
            new_tag = 'name'
            new_entity_xml_id = self.__db_handler.get_next_xml_id(entity_type)
            new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, new_tag)

            entity_object = self.__db_handler.create_entity_object(entity_type, new_entity_xml_id)
            entity_version_object = self.__db_handler.create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__db_handler.create_entity_properties_objects(entity_type, entity_properties, entity_version_object)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id, new_entity_xml_id,
                                                                         old_entity_xml_id, self.__annotator_xml_id,
                                                                         new_tag, new_tag_xml_id)

            self.__db_handler.set_body_content(body_content)

            last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

            if last_reference:
                self.__db_handler.mark_entity_to_delete(old_entity_xml_id)

        elif not new_entity_xml_id and entity_type not in self.__listable_entities_types:
            new_entity_xml_id = self.__db_handler.get_next_xml_id(entity_type)

            entity_object = self.__db_handler.create_entity_object(entity_type, new_entity_xml_id)
            entity_version_object = self.__db_handler.create_entity_version_object(entity_object)

            entity_properties = request['parameters']['entity_properties']
            self.__db_handler.create_entity_properties_objects(entity_type, entity_properties, entity_version_object)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id, new_entity_xml_id,
                                                                         old_entity_xml_id, self.__annotator_xml_id,
                                                                         entity_type, new_entity_xml_id)

            entity_properties.pop('name', '')

            body_content = self.__xml_handler.add_attributes_to_tag(body_content, new_entity_xml_id, entity_properties)

            self.__db_handler.set_body_content(body_content)

            last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

            if last_reference:
                self.__db_handler.mark_entity_to_delete(old_entity_xml_id)

        elif new_entity_xml_id and entity_type in self.__listable_entities_types:
            new_tag = 'name'
            new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, new_tag)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id, new_entity_xml_id,
                                                                         old_entity_xml_id, self.__annotator_xml_id,
                                                                         new_tag, new_tag_xml_id)

            self.__db_handler.set_body_content(body_content)

            last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

            if last_reference:
                self.__db_handler.mark_entity_to_delete(old_entity_xml_id)

        elif new_entity_xml_id and entity_type not in self.__listable_entities_types:
            new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, entity_type)

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id, new_entity_xml_id,
                                                                         old_entity_xml_id, self.__annotator_xml_id,
                                                                         entity_type, new_tag_xml_id)

            self.__db_handler.set_body_content(body_content)

            last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

            if last_reference:
                self.__db_handler.mark_entity_to_delete(old_entity_xml_id)

        else:
            raise BadRequest("There is no operation matching to this request")

    def __get_new_tag_xml_id(self, tag_xml_id, new_tag):
        edited_element_id_base = tag_xml_id.split('-')[0]

        if edited_element_id_base != new_tag:
            new_tag_xml_id = self.__db_handler.get_next_xml_id('name')
        else:
            new_tag_xml_id = None

        return new_tag_xml_id

    def __delete_reference_to_entity(self, request):
        # TODO: add attribute `newId="ab-XX"`, when tag name will be changed to 'ab'

        tag_xml_id = request.get('edited_element_id')
        entity_xml_id = request.get('old_element_id')

        body_content = self.__db_handler.get_body_content()

        body_content = self.__xml_handler.mark_reference_to_delete(body_content, tag_xml_id, entity_xml_id,
                                                                   self.__annotator_xml_id)

        self.__db_handler.set_body_content(body_content)

        last_reference = self.__xml_handler.check_if_last_reference(body_content, entity_xml_id)

        if last_reference:
            self.__db_handler.mark_entity_to_delete(entity_xml_id)

    def __add_entity_property(self, request):
        entity_xml_id = request['edited_element_id']
        entity_property = request['parameters']
        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.add_entity_property(entity_xml_id, entity_property)

        else:
            self.__db_handler.add_entity_property(entity_xml_id, entity_property)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.add_entity_property(body_content, entity_xml_id, entity_property)
            self.__db_handler.set_body_content(body_content)

    def __delete_entity_property(self, request):
        entity_xml_id = request.get('edited_element_id')
        entity = self.__db_handler.get_entity_from_db(entity_xml_id)

        if entity.type in self.__listable_entities_types:
            property_name = request['old_element_id']

            self.__db_handler.mark_entity_property_to_delete(entity_xml_id, property_name)

        else:
            property_name = request['old_element_id']

            self.__db_handler.mark_entity_property_to_delete(entity_xml_id, property_name)

            entity_property = self.__db_handler.get_entity_property_from_db(entity_xml_id, property_name, saved=True,
                                                                            deleted=True)
            property_value = entity_property.get_value(as_str=True)

            properties_to_delete = {property_name: property_value}

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.mark_properties_to_delete(body_content, entity_xml_id,
                                                                        properties_to_delete, self.__annotator_xml_id)

            self.__db_handler.set_body_content(body_content)

    def __modify_entity_property(self, request):
        entity_xml_id = request['edited_element_id']
        entity = self.__db_handler.get_entity_from_db(entity_xml_id)

        if entity.type in self.__listable_entities_types:
            property_name = request['old_element_id']

            self.__db_handler.mark_entity_property_to_delete(entity_xml_id, property_name)

            entity_property = request['parameters']

            entity_version_object = self.__db_handler.get_entity_version_from_db(entity_xml_id)

            self.__db_handler.create_entity_properties_objects(entity.type, entity_property, entity_version_object)

        else:
            property_name = request['old_element_id']

            self.__db_handler.mark_entity_property_to_delete(entity_xml_id, property_name)

            entity_property = request['parameters']

            entity_version_object = self.__db_handler.get_entity_version_from_db(entity_xml_id)

            self.__db_handler.create_entity_properties_objects(entity.type, entity_property, entity_version_object)

            entity_property_object = self.__db_handler.get_entity_property_from_db(entity_xml_id, property_name,
                                                                                   saved=True, deleted=True)

            property_value = entity_property_object.get_value(as_str=True)

            properties_to_delete = {property_name: property_value}

            body_content = self.__db_handler.get_body_content()

            body_content = self.__xml_handler.mark_properties_to_delete(body_content, entity_xml_id,
                                                                        properties_to_delete, self.__annotator_xml_id)

            body_content = self.__xml_handler.add_properties_to_tag(body_content, entity_xml_id, entity_property)

            self.__db_handler.set_body_content(body_content)

    def __add_certainty(self, request):
        certainty_target = request['new_element_id']
        parameters = request['parameters']

        self.__db_handler.add_certainty(certainty_target, parameters)

    def __modify_certainty(self, request):
        certainty_xml_id = request['edited_element_id']
        parameter_name = request['old_element_id']
        new_value = request['parameters']

        self.__db_handler.modify_certainty(certainty_xml_id, parameter_name, new_value)

    def __delete_certainty(self, request):
        certainty_xml_id = request['edited_element_id']

        self.__db_handler.delete_certainty(certainty_xml_id)
