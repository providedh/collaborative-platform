from django.forms.models import model_to_dict

from apps.api_vis.models import Certainty, Entity, EntityProperty, EntityVersion
from apps.close_reading.enums import ElementTypes
from apps.close_reading.models import AnnotatingBodyContent, Operation
from apps.close_reading.response_generator import get_custom_entities_types
from apps.exceptions import BadParameters
from apps.files_management.models import File, FileMaxXmlIds
from apps.projects.models import UncertaintyCategory

from collaborative_platform.settings import CUSTOM_ENTITY, DEFAULT_ENTITIES


class DbHandler:
    def __init__(self, user, file_id):
        self.__user = user
        self.__file = self.get_file_from_db(file_id)
        self.__custom_entities_types = get_custom_entities_types(self.__file.project)
        self.__annotating_body_content = self.__get_body_content_from_db()

    def add_entity(self, entity_type, entity_properties):
        entity_xml_id = self.get_next_xml_id(entity_type)

        entity = self.__create_entity_object(entity_type, entity_xml_id)
        entity_version = self.__create_entity_version_object(entity)

        self.__create_entity_properties_objects(entity_version, entity_properties)

        return entity_xml_id

    def delete_entity(self, entity_xml_id):
        entity = self.__get_entity_from_db(entity_xml_id)
        self.__mark_entity_to_delete(entity)

        entity_version = self.__get_entity_version_from_db(entity_xml_id)
        self.__mark_entity_properties_to_delete(entity_version)

        certainties = Certainty.objects.filter(
            file_version=self.__file.file_versions.order_by('-number')[0],
            target_xml_id=entity_xml_id
        )

        for certainty in certainties:
            certainty.deleted_by = self.__user

        Certainty.objects.bulk_update(certainties, ['deleted_by'])

    def add_entity_property(self, entity_xml_id, entity_property):
        entity_version = self.__get_entity_version_from_db(entity_xml_id)

        self.__create_entity_properties_objects(entity_version, entity_property)

        property_name = list(entity_property.keys())[0]
        property_id = f'{entity_xml_id}/{property_name}'

        return property_id

    def modify_entity_property(self, entity_xml_id, entity_property, property_name):
        entity_property_object = self.__get_entity_property_from_db(entity_xml_id, property_name)

        if entity_property_object.entity_version is not None:
            entity_property_object = self.__clone_entity_property(entity_property_object)

        for key, value in entity_property.items():
            entity_property_object.set_value(value)

        entity_property_object.save()

        property_name = list(entity_property.keys())[0]
        property_id = f'{entity_xml_id}/{property_name}'

        return property_id

    def delete_entity_property(self, entity_xml_id, property_name):
        entity_version = self.__get_entity_version_from_db(entity_xml_id)

        self.__mark_entity_properties_to_delete(entity_version, [property_name])

    def add_certainty(self, certainty_target, parameters):
        locus = parameters['locus']

        target_type = self.__get_certainty_target_type(certainty_target, locus)
        target, match = self.__get_certainty_target_and_match(certainty_target, target_type)

        xml_id = self.get_next_xml_id('certainty')

        certainty_object = Certainty.objects.create(
            file=self.__file,
            xml_id=xml_id,
            locus=parameters.get('locus'),
            cert=parameters.get('certainty'),
            target_xml_id=target,
            target_match=match,
            asserted_value=parameters.get('asserted_value'),
            description=parameters.get('description'),
            created_by=self.__user
        )

        categories = parameters.get('categories')
        categories_ids = self.__get_categories_ids_from_db(categories)

        certainty_object.categories.add(*categories_ids)

        return xml_id

    def modify_certainty(self, certainty_xml_id, parameter_name, parameters):
        certainty = self.__get_certainty_from_db(certainty_xml_id)

        if certainty.file_version is not None:
            certainty = self.__clone_certainty(certainty)

        if parameter_name == 'categories':
            categories = certainty.categories.all()

            for category in categories:
                certainty.categories.remove(category)

            categories = parameters.get('categories')
            categories_ids = self.__get_categories_ids_from_db(categories)

            certainty.categories.add(*categories_ids)

        elif parameter_name == 'locus':
            locus = parameters.get('locus')
            certainty.locus = locus
            certainty.save()

        elif parameter_name == 'certainty':
            cert = parameters.get('certainty')
            certainty.cert = cert
            certainty.save()

        elif parameter_name == 'asserted_value':
            asserted_value = parameters.get('asserted_value')
            certainty.asserted_value = asserted_value
            certainty.save()

        elif parameter_name == 'description':
            description = parameters.get('description')
            certainty.description = description
            certainty.save()

        elif parameter_name == 'reference':
            certainty_target = parameters['new_element_id']
            locus = parameters['locus']

            target_type = self.__get_certainty_target_type(certainty_target, locus)
            target, match = self.__get_certainty_target_and_match(certainty_target, target_type)

            certainty.target_xml_id = target
            certainty.target_match = match
            certainty.save()

    def delete_certainty(self, certainty_xml_id):
        certainty = self.__get_certainty_from_db(certainty_xml_id)

        self.__mark_certainty_to_delete(certainty)

    @staticmethod
    def get_file_from_db(file_id):
        file = File.objects.get(id=file_id, deleted=False)

        return file

    def get_entity_type(self, entity_xml_id):
        entity = self.__get_entity_from_db(entity_xml_id)
        entity_type = entity.type

        return entity_type

    def get_entity_property_value(self, entity_xml_id, property_name):
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name)

        entity_property_value = entity_property.get_value(as_str=True)

        return entity_property_value

    def get_next_xml_id(self, entity_type):
        entity_max_xml_id = FileMaxXmlIds.objects.get(
            file=self.__file,
            xml_id_base=entity_type,
        )

        xml_id_nr = entity_max_xml_id.get_next_number()
        xml_id = f'{entity_type}-{xml_id_nr}'

        return xml_id

    def get_annotator_xml_id(self):
        annotator_xml_id = self.__user.profile.get_xml_id()

        return annotator_xml_id

    def get_body_content(self):
        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        return body_content

    def set_body_content(self, body_content):
        self.__annotating_body_content.body_content = body_content
        self.__annotating_body_content.save()

    def __create_entity_object(self, entity_type, xml_id):
        entity_object = Entity.objects.create(
            file=self.__file,
            type=entity_type,
            xml_id=xml_id,
            created_by=self.__user,
        )

        return entity_object

    @staticmethod
    def __create_entity_version_object(entity_object):
        entity_version_object = EntityVersion.objects.create(
            entity=entity_object,
        )

        return entity_version_object

    def __create_entity_properties_objects(self, entity_version, entity_properties):
        if entity_version.entity.type in DEFAULT_ENTITIES.keys():
            properties = DEFAULT_ENTITIES[entity_version.entity.type]['properties']
        else:
            properties = CUSTOM_ENTITY['properties']

        properties_objects = []

        for name, value in entity_properties.items():
            entity_property_object = EntityProperty(
                entity=entity_version.entity,
                xpath='',
                name=name,
                type=properties[name]['type'],
                created_by=self.__user,
            )

            entity_property_object.set_value(value)

            properties_objects.append(entity_property_object)

        EntityProperty.objects.bulk_create(properties_objects)

    def __mark_entity_to_delete(self, entity):
        entity.deleted_by = self.__user
        entity.save()

    def __mark_entity_property_to_delete(self, entity_property):
        entity_property.deleted_by = self.__user
        entity_property.save()

    def __mark_certainty_to_delete(self, certainty):
        certainty.deleted_by = self.__user
        certainty.save()

    def __mark_entity_properties_to_delete(self, entity_version, entity_properties_names=None):
        # TODO: Add marking certainties to properties to delete

        if entity_properties_names:
            entity_properties = EntityProperty.objects.filter(
                entity_version=entity_version,
                name__in=entity_properties_names
            )

        else:
            entity_properties = EntityProperty.objects.filter(
                entity_version=entity_version
            )

        for entity_property in entity_properties:
            entity_property.deleted_by = self.__user

        EntityProperty.objects.bulk_update(entity_properties, ['deleted_by'])

    def __get_entity_from_db(self, entity_xml_id):
        entity = Entity.objects.get(
            file=self.__file,
            xml_id=entity_xml_id
        )

        return entity

    def __get_entity_version_from_db(self, entity_xml_id):
        try:
            entity_version = EntityVersion.objects.get(
                entity__xml_id=entity_xml_id,
                file_version__isnull=True
            )
        except EntityVersion.DoesNotExist:
            file_version = self.__get_file_version()

            entity_version = EntityVersion.objects.get(
                entity__xml_id=entity_xml_id,
                file_version=file_version
            )

        return entity_version

    def __get_entity_property_from_db(self, entity_xml_id, property_name):
        try:
            entity_property = EntityProperty.objects.get(
                entity__xml_id=entity_xml_id,
                name=property_name,
                entity_version__isnull=True
            )
        except EntityProperty.DoesNotExist:
            entity_version = self.__get_entity_version_from_db(entity_xml_id)

            entity_property = EntityProperty.objects.get(
                entity__xml_id=entity_xml_id,
                name=property_name,
                entity_version=entity_version
            )

        return entity_property

    def __get_certainty_from_db(self, certainty_xml_id):
        try:
            certainty = Certainty.objects.get(
                xml_id=certainty_xml_id,
                file_version__isnull=True
            )
        except Certainty.DoesNotExist:
            file_version = self.__get_file_version()

            certainty = Certainty.objects.get(
                xml_id=certainty_xml_id,
                file_version=file_version
            )

        return certainty

    def __get_file_version(self):
        version_number = self.__file.version_number
        file_version = self.__file.file_versions.get(number=version_number)

        return file_version

    def __clone_entity_property(self, entity_property):  # type: (EntityProperty) -> EntityProperty
        self.__mark_entity_property_to_delete(entity_property)

        entity_property.id = None
        entity_property.created_in_file_version = None
        entity_property.deleted_by = None
        entity_property.entity_version = None
        entity_property.save()

        return entity_property

    def __clone_certainty(self, certainty):
        self.__mark_certainty_to_delete(certainty)

        certainty_categories = certainty.categories.all()

        certainty.id = None
        certainty.created_in_file_version = None
        certainty.deleted_by = None
        certainty.file_version = None
        certainty.save()

        for category in certainty_categories:
            certainty.categories.add(category)

        return certainty

    def __get_categories_ids_from_db(self, categories):
        categories = UncertaintyCategory.objects.filter(
            taxonomy__project=self.__file.project,
            name__in=categories
        )

        categories_ids = categories.values_list('id', flat=True)

        return categories_ids

    def __get_body_content_from_db(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

        return annotating_body_content

    @staticmethod
    def __get_certainty_target_type(certainty_target, locus):
        if 'certainty-' in certainty_target:
            target_type = ElementTypes.certainty
        elif '/' in certainty_target:
            target_type = ElementTypes.entity_property
        elif '@ref' in certainty_target:
            target_type = ElementTypes.reference
        elif locus == 'value':
            target_type = ElementTypes.text
        elif locus == 'name':
            target_type = ElementTypes.entity_type
        else:
            raise BadParameters("There is no 'target type' matching to given parameters")

        return target_type

    def __get_certainty_target_and_match(self, certainty_target, target_type):
        if target_type == ElementTypes.text:
            target = certainty_target
            match = None

        elif target_type == ElementTypes.reference:
            target = certainty_target.split('@')[0]
            match = '@ref'

        elif target_type == ElementTypes.entity_type:
            entity = Entity.objects.get(
                xml_id=certainty_target,
                file=self.__file
            )

            if entity.type not in self.__custom_entities_types:
                target = certainty_target
                match = None
            else:
                target = certainty_target
                match = '@type'

        elif target_type == ElementTypes.entity_property:
            target = certainty_target.split('/')[0]
            property_name = certainty_target.split('/')[1]

            entity_property = self.__get_entity_property_from_db(target, property_name)
            match = entity_property.xpath

        elif target_type == ElementTypes.certainty:
            target = certainty_target
            match = None

        else:
            raise BadParameters("There is no 'target' and 'match' matching to given parameters")

        return target, match

    def get_operations_from_db(self, operations_ids):
        operations = Operation.objects.filter(
            user=self.__user,
            id__in=operations_ids
        ).order_by('id')

        operations = [model_to_dict(operation) for operation in operations]

        return operations

    def add_operation(self, operation, operation_result):
        Operation.objects.get_or_create(
            user=self.__user,
            file=self.__file,
            method=operation['method'],
            element_type=operation['element_type'],
            edited_element_id=operation.get('edited_element_id'),
            old_element_id=operation.get('old_element_id'),
            new_element_id=operation.get('new_element_id'),
            operation_result=operation_result,
        )

    @staticmethod
    def delete_operation(operation_id):
        operation = Operation.objects.get(
            id=operation_id
        )

        operation.delete()
