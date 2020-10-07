import copy

from django.db.models import Q
from django.forms.models import model_to_dict

from apps.api_vis.models import Certainty, Entity, EntityProperty, EntityVersion
from apps.close_reading.enums import ElementTypes
from apps.close_reading.models import AnnotatingBodyContent, Operation
from apps.close_reading.response_generator import get_custom_entities_types
from apps.exceptions import BadParameters, Forbidden, UnsavedElement
from apps.files_management.api import clone_db_objects
from apps.files_management.helpers import create_uploaded_file_object_from_string, hash_file
from apps.files_management.models import File, FileMaxXmlIds, FileVersion
from apps.projects.helpers import log_activity, create_new_project_version
from apps.projects.models import UncertaintyCategory

from collaborative_platform.settings import CUSTOM_ENTITY, DEFAULT_ENTITIES


class DbHandler:
    def __init__(self, user, file_id):
        self.__user = user
        self.__file = self.get_file_from_db(file_id)
        self.__custom_entities_types = get_custom_entities_types(self.__file.project)
        self.__annotating_body_content = self.__get_body_content_from_db()

    def add_entity(self, entity_type):
        entity_xml_id = self.get_next_xml_id(entity_type)

        entity = self.__create_entity_object(entity_type, entity_xml_id)
        self.__create_entity_version_object(entity)

        return entity_xml_id

    def delete_entity(self, entity_xml_id):
        entity = self.__get_entity_from_db(entity_xml_id)

        try:
            self.check_if_entity_is_saved(entity_xml_id)

        except UnsavedElement:
            self.__clean_up_entity(entity)

        else:
            self.__mark_entity_to_delete(entity)

            entity_version = self.__get_entity_version_from_db(entity_xml_id)
            self.__mark_entity_properties_to_delete(entity_version)

            self.__mark_certainties_to_delete(entity_xml_id)

    def add_entity_property(self, entity_xml_id, entity_property):
        entity_version = self.__get_entity_version_from_db(entity_xml_id)

        self.__create_entity_properties_objects(entity_version, entity_property)

        property_name = list(entity_property.keys())[0]
        property_id = f'{entity_xml_id}/{property_name}'

        return property_id

    def modify_entity_property(self, entity_xml_id, property_value, property_name):
        saved = False
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved)

        if not entity_property:
            saved = True
            entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved)
            entity_property = self.__clone_entity_property(entity_property)

        for key, value in property_value.items():
            entity_property.set_value(value)

        entity_property.save()

        property_id = f'{entity_xml_id}/{property_name}'

        return property_id, saved

    def delete_entity_property(self, entity_xml_id, property_name):
        self.check_if_entity_property_is_saved(entity_xml_id, property_name)

        entity_version = self.__get_entity_version_from_db(entity_xml_id)

        self.__mark_entity_properties_to_delete(entity_version, [property_name])

    def add_certainty(self, certainty_target, parameters):
        locus = parameters['locus']

        target_type = self.get_certainty_target_type(certainty_target, locus)
        target, match = self.get_certainty_target_and_match(certainty_target, target_type)

        xml_id = self.get_next_xml_id('certainty')

        certainty_object = Certainty.objects.create(
            file=self.__file,
            xml_id=xml_id,
            locus=parameters.get('locus'),
            certainty=parameters.get('certainty'),
            target_xml_id=target,
            target_match=match,
            asserted_value=parameters.get('asserted_value') if parameters.get('asserted_value') else None,
            description=parameters.get('description') if parameters.get('description') else None,
            created_by=self.__user
        )

        categories = parameters.get('categories')
        categories_ids = self.__get_categories_ids_from_db(categories)

        certainty_object.categories.add(*categories_ids)

        return xml_id

    def modify_certainty(self, certainty_xml_id, parameter_name, parameters):
        saved = False
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved)

        if not certainty:
            saved = True
            certainty = self.__get_certainty_from_db(certainty_xml_id, saved)
            certainty = self.__clone_certainty(certainty)

        else:
            saved_certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)

            if saved_certainty:
                saved = True

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
            certainty_attribute = parameters.get('certainty')
            certainty.certainty = certainty_attribute
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

            target_type = self.get_certainty_target_type(certainty_target, locus)
            target, match = self.get_certainty_target_and_match(certainty_target, target_type)

            certainty.target_xml_id = target
            certainty.target_match = match
            certainty.save()

        return saved

    def delete_certainty(self, certainty_xml_id):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)

        if not certainty:
            raise UnsavedElement

        self.__mark_certainty_to_delete(certainty)

    def discard_adding_reference_to_entity(self, entity_xml_id, last_reference):
        if last_reference:
            entity_version = self.__get_entity_version_from_db(entity_xml_id, unsaved=True)

            if entity_version:
                entity_version.delete()

            entity = self.__get_entity_from_db(entity_xml_id)

            if entity.created_in_file_version is None:
                entity.delete()

    def discard_modifying_reference_to_entity(self, old_entity_xml_id, new_entity_xml_id, last_reference):
        if last_reference:
            new_entity_version = self.__get_entity_version_from_db(new_entity_xml_id, unsaved=True)

            if new_entity_version:
                new_entity_version.delete()

            new_entity = self.__get_entity_from_db(new_entity_xml_id)

            if new_entity.created_in_file_version is None:
                new_entity.delete()

        old_entity = self.__get_entity_from_db(old_entity_xml_id)
        self.__unmark_entity_to_delete(old_entity)

        old_entity_version = self.__get_entity_version_from_db(old_entity_xml_id)
        self.__unmark_entity_properties_to_delete(old_entity_version)

        self.__unmark_certainties_to_delete(old_entity_xml_id)

    def discard_removing_reference_to_entity(self, old_entity_xml_id):
        old_entity = self.__get_entity_from_db(old_entity_xml_id)
        self.__unmark_entity_to_delete(old_entity)

        old_entity_version = self.__get_entity_version_from_db(old_entity_xml_id)
        self.__unmark_entity_properties_to_delete(old_entity_version)

        self.__unmark_certainties_to_delete(old_entity_xml_id)

    def discard_adding_entity_property(self, entity_xml_id, property_name):
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=False)
        entity_property.delete()

    def discard_modifying_entity_property(self, entity_xml_id, property_name):
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=False)
        entity_property.delete()

        entity_version = self.__get_entity_version_from_db(entity_xml_id)
        self.__unmark_entity_properties_to_delete(entity_version, [property_name])

    def discard_removing_entity_property(self, entity_xml_id, property_name):
        entity_version = self.__get_entity_version_from_db(entity_xml_id)
        self.__unmark_entity_properties_to_delete(entity_version, [property_name])

    def discard_adding_certainty(self, certainty_xml_id):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=False)
        certainty.delete()

    def discard_modifying_certainty(self, certainty_xml_id):
        new_certainty = self.__get_certainty_from_db(certainty_xml_id, saved=False)
        new_certainty.delete()

        old_certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)
        self.__unmark_entity_to_delete(old_certainty)

    def discard_removing_certainty(self, certainty_xml_id):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)
        self.__unmark_certainty_to_delete(certainty)

    def accept_adding_reference_to_entity(self, entity_xml_id, new_file_version):
        entity = self.__get_entity_from_db(entity_xml_id)

        if entity.created_in_file_version is None:
            self.__confirm_entity_creation(entity, new_file_version)

    def accept_modifying_reference_to_entity(self, old_entity_xml_id, new_entity_xml_id, new_file_version,
                                             last_reference):
        entity = self.__get_entity_from_db(new_entity_xml_id)

        if entity.created_in_file_version is None:
            self.__confirm_entity_creation(entity, new_file_version)

            new_entity_version = self.__get_entity_version_from_db(new_entity_xml_id, new_file_version)
            self.__confirm_entity_properties_creation(new_entity_version, new_file_version)

        if last_reference:
            old_entity = self.__get_entity_from_db(old_entity_xml_id)
            self.__confirm_entity_delete(old_entity, new_file_version)

            old_entity_version = self.__get_entity_version_from_db(old_entity_xml_id)
            self.__confirm_entity_properties_delete(old_entity_version, new_file_version)

            self.__confirm_certainties_delete(old_entity_xml_id, new_file_version)

    def accept_removing_reference_to_entity(self, entity_xml_id, new_file_version, last_reference):
        if last_reference:
            entity = self.__get_entity_from_db(entity_xml_id)
            self.__confirm_entity_delete(entity, new_file_version)

            old_entity_version = self.__get_entity_version_from_db(entity_xml_id)
            self.__confirm_entity_properties_delete(old_entity_version, new_file_version)

            self.__confirm_certainties_delete(entity_xml_id, new_file_version)

    def accept_adding_entity_property(self, entity_xml_id, property_name, new_file_version):
        entity_version = self.__get_entity_version_from_db(entity_xml_id, new_file_version)

        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=False)
        entity_property.created_in_file_version = new_file_version
        entity_property.entity_version = entity_version
        entity_property.save()

    def accept_modifying_entity_property(self, entity_xml_id, property_name, new_file_version):
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=False)
        entity_property.created_in_file_version = new_file_version
        entity_property.save()

        entity_version = self.__get_entity_version_from_db(entity_xml_id)
        self.__confirm_entity_properties_delete(entity_version, new_file_version, [property_name])

    def accept_removing_entity_property(self, entity_xml_id, property_name, new_file_version):
        entity_version = self.__get_entity_version_from_db(entity_xml_id)
        self.__confirm_entity_properties_delete(entity_version, new_file_version, [property_name])

    def accept_adding_certainty(self, certainty_xml_id, new_file_version):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=False)
        certainty.created_in_file_version = new_file_version
        certainty.file_version = new_file_version
        certainty.save()

    def accept_modifying_certainty(self, certainty_xml_id, new_file_version):
        old_certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)
        old_certainty.deleted_in_file_version = new_file_version
        old_certainty.save()

        new_certainty = self.__get_certainty_from_db(certainty_xml_id, saved=False)
        new_certainty.created_in_file_version = new_file_version
        new_certainty.file_version = new_file_version
        new_certainty.save()

    def accept_removing_certainty(self, certainty_xml_id, new_file_version):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)
        certainty.deleted_in_file_version = new_file_version
        certainty.save()

    def check_entity_permissions(self, entity_xml_id):
        entity = self.__get_entity_from_db(entity_xml_id)

        if entity.created_by != self.__user:
            raise Forbidden

    def check_certainty_permissions(self, certainty_xml_id):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)

        if not certainty:
            certainty = self.__get_certainty_from_db(certainty_xml_id, saved=False)

        if certainty.created_by != self.__user:
            raise Forbidden

    @staticmethod
    def get_file_from_db(file_id):
        file = File.objects.get(id=file_id, deleted=False)

        return file

    def get_entity_type(self, entity_xml_id):
        entity = self.__get_entity_from_db(entity_xml_id)
        entity_type = entity.type

        return entity_type

    def get_entity_properties_values(self, entity_xml_id, include_unsaved=False):
        entity_version = self.__get_entity_version_from_db(entity_xml_id)

        if include_unsaved:
            entity_properties = EntityProperty.objects.filter(
                Q(entity_version=entity_version)
                | (Q(entity=entity_version.entity) & Q(entity_version__isnull=True))
            )

        else:
            entity_properties = entity_version.properties.all()

        entity_properties = {property.name: property.get_value(as_str=True) for property in entity_properties}

        return entity_properties

    def get_entity_property_value(self, entity_xml_id, property_name):
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=False)

        if not entity_property:
            entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=True)

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
            xpath = properties[name]['xpath']
            xpath = self.__reformat_xpath(xpath)

            entity_property_object = EntityProperty(
                entity=entity_version.entity,
                name=name,
                xpath=xpath,
                type=properties[name]['type'],
                created_by=self.__user,
            )

            entity_property_object.set_value(value)

            properties_objects.append(entity_property_object)

        EntityProperty.objects.bulk_create(properties_objects)

    def __mark_entity_to_delete(self, entity):
        entity.deleted_by = self.__user
        entity.save()

    @staticmethod
    def __unmark_entity_to_delete(entity):
        entity.deleted_by = None
        entity.save()

    def __clean_up_entity(self, entity):
        certainties = Certainty.objects.filter(
            file=self.__file,
            target_xml_id=entity.xml_id
        )

        for certainty in certainties:
            certainty.delete()

        entity.delete()

    def __confirm_entity_creation(self, entity, new_file_version):
        entity.created_in_file_version = new_file_version
        entity.save()

        entity_version = self.__get_entity_version_from_db(entity.xml_id, unsaved=True)
        entity_version.file_version = new_file_version
        entity_version.save()

    @staticmethod
    def __confirm_entity_delete(entity, new_file_version):
        entity.deleted_in_file_version = new_file_version
        entity.save()

    def __mark_entity_property_to_delete(self, entity_property):
        entity_property.deleted_by = self.__user
        entity_property.save()

    def __mark_certainty_to_delete(self, certainty):
        certainty.deleted_by = self.__user
        certainty.save()

    def __unmark_certainty_to_delete(self, certainty):
        certainty.deleted_by = None
        certainty.save()

    def __mark_certainties_to_delete(self, target_xml_id):
        file_version = self.__get_file_version()

        certainties = Certainty.objects.filter(
            file_version=file_version,
            target_xml_id=target_xml_id
        )

        for certainty in certainties:
            certainty.deleted_by = self.__user

        Certainty.objects.bulk_update(certainties, ['deleted_by'])

    def __unmark_certainties_to_delete(self, target_xml_id):
        file_version = self.__get_file_version()

        certainties = Certainty.objects.filter(
            file_version=file_version,
            target_xml_id=target_xml_id
        )

        for certainty in certainties:
            certainty.deleted_by = None

        Certainty.objects.bulk_update(certainties, ['deleted_by'])

    def __confirm_certainties_delete(self, target_xml_id, new_file_version):
        file_version = self.__get_file_version()

        certainties = Certainty.objects.filter(
            file_version=file_version,
            target_xml_id=target_xml_id
        )

        for certainty in certainties:
            certainty.deleted_in_file_version = new_file_version

        Certainty.objects.bulk_update(certainties, ['deleted_in_file_version'])

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

    @staticmethod
    def __unmark_entity_properties_to_delete(entity_version, entity_properties_names=None):
        # TODO: Add unmarking certainties to properties to delete

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
            entity_property.deleted_by = None

        EntityProperty.objects.bulk_update(entity_properties, ['deleted_by'])

    @staticmethod
    def __confirm_entity_properties_creation(entity_version, new_file_version, entity_properties_names=None):
        if entity_properties_names:
            entity_properties = EntityProperty.objects.filter(
                entity=entity_version.entity,
                name__in=entity_properties_names,
                created_in_file_version__isnull=True
            )

        else:
            entity_properties = EntityProperty.objects.filter(
                entity=entity_version.entity,
                created_in_file_version__isnull=True
            )

        for entity_property in entity_properties:
            entity_property.created_in_file_version = new_file_version
            entity_property.entity_version = entity_version

        EntityProperty.objects.bulk_update(entity_properties, ['created_in_file_version', 'entity_version'])

    @staticmethod
    def __confirm_entity_properties_delete(entity_version, new_file_version, entity_properties_names=None):
        # TODO: Add deleting certainties to properties

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
            entity_property.deleted_in_file_version = new_file_version

        EntityProperty.objects.bulk_update(entity_properties, ['deleted_in_file_version'])

    def __get_entity_from_db(self, entity_xml_id):
        entity = Entity.objects.get(
            file=self.__file,
            xml_id=entity_xml_id
        )

        return entity

    def check_if_entity_is_saved(self, entity_xml_id):
        entity = self.__get_entity_from_db(entity_xml_id)

        if entity.created_in_file_version is None:
            raise UnsavedElement

    def __get_entity_version_from_db(self, entity_xml_id, file_version=None, unsaved=False):
        if file_version:
            try:
                entity_version = EntityVersion.objects.get(
                    entity__xml_id=entity_xml_id,
                    file_version=file_version,
                )

            except EntityVersion.DoesNotExist:
                entity_version = None

        else:
            try:
                entity_version = EntityVersion.objects.get(
                    entity__xml_id=entity_xml_id,
                    file_version__isnull=True
                )

            except EntityVersion.DoesNotExist:
                if unsaved:
                    entity_version = None

                else:
                    file_version = self.__get_file_version()

                    entity_version = EntityVersion.objects.get(
                        entity__xml_id=entity_xml_id,
                        file_version=file_version
                    )

        return entity_version

    def __get_entity_property_from_db(self, entity_xml_id, property_name, saved=None):
        entity_property = None

        if saved is True:
            try:
                entity_version = self.__get_entity_version_from_db(entity_xml_id)

                entity_property = EntityProperty.objects.get(
                    entity__xml_id=entity_xml_id,
                    name=property_name,
                    entity_version=entity_version
                )
            except EntityProperty.DoesNotExist:
                pass

        elif saved is False:
            try:
                entity_property = EntityProperty.objects.get(
                    entity__xml_id=entity_xml_id,
                    name=property_name,
                    entity_version__isnull=True
                )
            except EntityProperty.DoesNotExist:
                pass

        else:
            raise ValueError("Value for 'saved' argument not provided")

        return entity_property

    def check_if_entity_property_is_saved(self, entity_xml_id, property_name):
        entity_property = self.__get_entity_property_from_db(entity_xml_id, property_name, saved=True)

        if not entity_property:
            raise UnsavedElement

    def __get_certainty_from_db(self, certainty_xml_id, saved=None):
        certainty = None

        if saved is True:
            try:
                file_version = self.__get_file_version()

                certainty = Certainty.objects.get(
                    xml_id=certainty_xml_id,
                    file_version=file_version
                )
            except Certainty.DoesNotExist:
                pass

        elif saved is False:
            try:
                certainty = Certainty.objects.get(
                    xml_id=certainty_xml_id,
                    file_version__isnull=True
                )
            except Certainty.DoesNotExist:
                pass

        else:
            raise ValueError("Value for 'saved' argument not provided")

        return certainty

    def check_if_certainty_is_saved(self, certainty_xml_id):
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved=True)

        if not certainty:
            raise UnsavedElement

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
        room_symbol = f'{self.__file.project.id}_{self.__file.id}'

        annotating_body_content = AnnotatingBodyContent.objects.get(room_symbol=room_symbol)

        return annotating_body_content

    @staticmethod
    def __reformat_xpath(match):
        match = match.replace('default:', '')
        match = match.replace('/text()', '')

        if match == '.':
            match = None

        return match

    @staticmethod
    def get_certainty_target_type(certainty_target, locus):
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

    def get_certainty_target_and_match(self, certainty_target, target_type):
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

            entity_property = self.__get_entity_property_from_db(target, property_name, saved=True)

            if not entity_property:
                entity_property = self.__get_entity_property_from_db(target, property_name, saved=False)

            match = entity_property.xpath

        elif target_type == ElementTypes.certainty:
            target = certainty_target
            match = None

        else:
            raise BadParameters("There is no 'target' and 'match' matching to given parameters")

        return target, match

    def get_certainty_locus(self, certainty_xml_id):
        saved = False
        certainty = self.__get_certainty_from_db(certainty_xml_id, saved)

        if not certainty:
            saved = True
            certainty = self.__get_certainty_from_db(certainty_xml_id, saved)

        return certainty.locus

    def get_operations(self, operations_ids, with_dependent=False, from_latest=False):
        operations = self.get_operations_from_db(operations_ids)

        if with_dependent:
            operations = self.__add_dependent_operations(operations)

        operations = [model_to_dict(operation) for operation in operations]
        operations = self.__sort_operations(operations, from_latest=from_latest)

        return operations

    def get_operations_from_db(self, operations_ids):
        operations = Operation.objects.filter(
            file=self.__file,
            user=self.__user,
            id__in=operations_ids
        ).order_by('id')

        return operations

    @staticmethod
    def __add_dependent_operations(operations):
        old_operations = set()
        new_operations = set(operations)

        while old_operations != new_operations:
            old_operations = copy.deepcopy(new_operations)
            new_operations = set()

            for operation in old_operations:
                new_operations.add(operation)

                dependent_operations = operation.operation_set.all()
                new_operations.update(dependent_operations)

        new_operations = list(new_operations)

        return new_operations

    def get_operation_dependencies_ids(self, operation_id):
        operation = Operation.objects.get(
            file=self.__file,
            id=operation_id,
        )
        dependencies = operation.dependencies.all()
        dependencies_ids = dependencies.values_list('id', flat=True)
        dependencies_ids = list(dependencies_ids)

        return dependencies_ids

    @staticmethod
    def __sort_operations(operations, from_latest=False):
        sorted_operations = sorted(operations, key=lambda k: k['id'], reverse=from_latest)

        return sorted_operations

    def add_operation(self, operation, operation_result, dependencies_ids):
        operation, created = Operation.objects.get_or_create(
            user=self.__user,
            file=self.__file,
            method=operation['method'],
            element_type=operation['element_type'],
            edited_element_id=operation.get('edited_element_id'),
            old_element_id=operation.get('old_element_id'),
            new_element_id=operation.get('new_element_id'),
            operation_result=operation_result,
        )

        operation.dependencies.add(*dependencies_ids)

    def update_operation(self, operation, operation_result, dependencies_ids):
        try:
            operation = Operation.objects.get(
                user=self.__user,
                file=self.__file,
                method='POST',
                element_type=operation['element_type'],
                edited_element_id=operation.get('edited_element_id'),
            )

            operation.operation_result = operation_result
            operation.save()

            dependencies = operation.dependencies.all()

            for dependency in dependencies:
                operation.dependencies.remove(dependency)

            operation.dependencies.add(*dependencies_ids)

        except Operation.DoesNotExist:
            pass

    @staticmethod
    def delete_operation(operation_id):
        operation = Operation.objects.get(
            id=operation_id
        )

        operation.delete()

    def get_new_file_version(self):
        new_file_version = FileVersion(
            file=self.__file,
            number=self.__file.version_number + 1,
            created_by=self.__user,
        )

        new_file_version.save(create_new_project_version=False)

        return new_file_version

    def get_previous_xml_content(self):
        file_version = self.__file.file_versions.order_by('-number')[1]
        xml_content = file_version.get_raw_content()

        return xml_content

    def finish_creating_new_file_version(self, new_file_version, new_xml_content):
        uploaded_file = create_uploaded_file_object_from_string(new_xml_content, self.__file.name)
        hash = hash_file(self.__file, uploaded_file)

        uploaded_file.name = hash

        new_file_version.upload = uploaded_file
        new_file_version.hash = hash
        new_file_version.save()

        self.__file.version_number = new_file_version.number
        self.__file.save()

        clone_db_objects(self.__file)

        project = self.__file.project
        create_new_project_version(project=project, files_modification=True)

        log_text = f"created version number {new_file_version.number} of"

        log_activity(self.__file.project, self.__user, log_text, self.__file)

    def get_operation_id_that_created_tag(self, tag_xml_id):
        operation = Operation.objects.get(
            file=self.__file,
            method='POST',
            operation_result=tag_xml_id,
        )

        return operation.id

    def get_operation_id_that_created_entity(self, entity_xml_id):
        operation = Operation.objects.get(
            file=self.__file,
            method='POST',
            new_element_id__isnull=True,
            operation_result=entity_xml_id
        )

        return operation.id

    def get_operation_id_that_created_reference(self, tag_xml_id):
        operation = Operation.objects.get(
            file=self.__file,
            method='POST',
            element_type='reference',
            edited_element_id=tag_xml_id
        )

        return operation.id

    def get_operation_id_that_created_entity_property(self, entity_xml_id, property_name):
        try:
            operation = Operation.objects.get(
                file=self.__file,
                method='POST',
                element_type='entity_property',
                operation_result=f'{entity_xml_id}/{property_name}'
            )

        except Operation.DoesNotExist:
            operation = Operation.objects.get(
                file=self.__file,
                method='POST',
                new_element_id__isnull=True,
                operation_result=entity_xml_id
            )

        return operation.id

    def get_operation_id_that_created_certainty(self, certainty_xml_id):
        operation = Operation.objects.get(
            file=self.__file,
            method='POST',
            element_type='certainty',
            operation_result=certainty_xml_id
        )

        return operation.id
