import json

from apps.api_vis.models import Entity, EntityProperty, EntityVersion, Certainty
from apps.close_reading.db_handler import DbHandler
from apps.close_reading.enums import TargetTypes
from apps.close_reading.response_generator import get_custom_entities_types, get_listable_entities_types, \
    get_unlistable_entities_types
from apps.close_reading.xml_handler import XmlHandler
from apps.exceptions import BadRequest, NotModified
from apps.projects.models import UncertaintyCategory

from collaborative_platform.settings import XML_NAMESPACES


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class RequestHandler:
    def __init__(self, user, file_id):
        self.__db_handler = DbHandler(user, file_id)
        self.__file = self.__db_handler.get_file_from_db(file_id)
        self.__annotator_xml_id = self.__db_handler.get_annotator_xml_id()

        self.__listable_entities_types = get_listable_entities_types(self.__file.project)
        self.__unlistable_entities_types = get_unlistable_entities_types(self.__file.project)
        self.__custom_entities_types = get_custom_entities_types(self.__file.project)

        self.__xml_handler = XmlHandler(self.__listable_entities_types, self.__unlistable_entities_types,
                                        self.__custom_entities_types)

    def handle_request(self, text_data, user):
        requests = self.__parse_text_data(text_data)

        for request in requests:
            if request['element_type'] == 'tag':
                if request['method'] == 'POST':
                    self.__add_new_tag_to_text(request)
                elif request['method'] == 'PUT':
                    self.__move_tag_to_new_position(request)
                elif request['method'] == 'DELETE':
                    self.__mark_tag_to_delete(request)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'reference':
                if request['method'] == 'POST':
                    self.__add_reference_to_entity(request)
                elif request['method'] == 'PUT':
                    self.__modify_reference_to_entity(request)
                elif request['method'] == 'DELETE':
                    self.__mark_reference_to_delete(request)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif request['element_type'] == 'entity_property':
                if request['method'] == 'POST':
                    self.__add_property_to_entity(request)
                elif request['method'] == 'PUT':
                    self.__modify_entity_property(request, user)
                elif request['method'] == 'DELETE':
                    self.__mark_property_to_delete(request)
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

    @staticmethod
    def __parse_text_data(text_data):
        request = json.loads(text_data)

        return request

    def __add_new_tag_to_text(self, request):
        # TODO: Add verification if this same tag not existing already
        # TODO: Add possibility to add tag if text fragment is separated by another tag

        body_content = self.__db_handler.get_body_content()
        start_pos = request['parameters']['start_pos']
        end_pos = request['parameters']['end_pos']
        tag_xml_id = self.__db_handler.get_next_xml_id('ab')

        body_content = self.__xml_handler.add_new_tag_to_text(body_content, start_pos, end_pos, tag_xml_id,
                                                              self.__annotator_xml_id)

        self.__db_handler.set_body_content(body_content)

    def __move_tag_to_new_position(self, request):
        # TODO: Add verification if user has rights to edit a tag
        # TODO: Add verification if tag wasn't moved by another user in the meantime

        body_content = self.__db_handler.get_body_content()
        new_start_pos = request['parameters']['new_start_pos']
        new_end_pos = request['parameters']['new_end_pos']
        tag_xml_id = request.get('edited_element_id')

        body_content = self.__xml_handler.move_tag_to_new_position(body_content, new_start_pos, new_end_pos, tag_xml_id,
                                                                   self.__annotator_xml_id)

        self.__db_handler.set_body_content(body_content)

    def __mark_tag_to_delete(self, request):
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

            body_content = self.__xml_handler.add_properties_to_tag(body_content, entity_xml_id, entity_properties,
                                                                    self.__annotator_xml_id)

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

    def __mark_reference_to_delete(self, request):
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

    def __add_property_to_entity(self, request):
        entity_xml_id = request.get('edited_element_id')
        entity = self.__db_handler.get_entity_from_db(entity_xml_id)

        if entity.type in self.__listable_entities_types:
            entity_properties = request['parameters']

            entity_version_object = self.__db_handler.get_entity_version_from_db(entity_xml_id)

            self.__db_handler.create_entity_properties_objects(entity.type, entity_properties, entity_version_object)

        else:
            entity_properties = request['parameters']

            entity_version_object = self.__db_handler.get_entity_version_from_db(entity_xml_id)

            self.__db_handler.create_entity_properties_objects(entity.type, entity_properties, entity_version_object)

            body_content = self.__db_handler.get_body_content()

            entity_properties.pop('name', '')

            body_content = self.__xml_handler.add_properties_to_tag(body_content, entity_xml_id, entity_properties,
                                                                    self.__annotator_xml_id)

            self.__db_handler.set_body_content(body_content)

    def __mark_property_to_delete(self, request):
        entity_xml_id = request.get('edited_element_id')
        entity = self.__db_handler.get_entity_from_db(entity_xml_id)

        if entity.type in self.__listable_entities_types:
            property_name = request['old_element_id']

            self.__db_handler.mark_entity_property_to_delete(entity_xml_id, property_name)

        else:
            property_name = request['old_element_id']

            entity_property = EntityProperty.objects.filter(
                entity_version__entity__xml_id=entity_xml_id,
                name=property_name,
            ).order_by('-id')[0]

            entity_property.deleted_by = user
            entity_property.save()

            property_value = entity_property.get_value(as_str=True)

            attributes_to_add = {
                f'{property_name}Deleted': property_value
            }

            attributes_to_delete = {
                property_name: property_value
            }

            self.__update_tag_in_body(entity_xml_id, attributes_to_add=attributes_to_add,
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
