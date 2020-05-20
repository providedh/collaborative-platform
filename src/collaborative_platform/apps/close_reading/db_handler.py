from apps.api_vis.models import Certainty, Entity, EntityProperty, EntityVersion
from apps.close_reading.models import AnnotatingBodyContent
from apps.files_management.models import File, FileMaxXmlIds

from collaborative_platform.settings import CUSTOM_ENTITY, DEFAULT_ENTITIES


class DbHandler:
    def __init__(self, user, file_id):
        self.__user = user
        self.__file = self.get_file_from_db(file_id)
        self.__annotating_body_content = self.__get_body_content_from_db()

    @staticmethod
    def get_file_from_db(file_id):
        file = File.objects.get(id=file_id, deleted=False)

        return file

    def __get_body_content_from_db(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

        return annotating_body_content

    def get_body_content(self):
        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        return body_content

    def set_body_content(self, body_content):
        self.__annotating_body_content.body_content = body_content
        self.__annotating_body_content.save()

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

    def create_entity_object(self, entity_type, xml_id):
        entity_object = Entity.objects.create(
            file=self.__file,
            type=entity_type,
            xml_id=xml_id,
            created_by=self.__user,
        )

        return entity_object

    @staticmethod
    def create_entity_version_object(entity_object):
        entity_version_object = EntityVersion.objects.create(
            entity=entity_object,
        )

        return entity_version_object

    def create_entity_properties_objects(self, entity_type, entity_properties, entity_version_object):
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
                created_by=self.__user,
            )

            entity_property_object.set_value(value)

            properties_objects.append(entity_property_object)

        EntityProperty.objects.bulk_create(properties_objects)

    def mark_entity_to_delete(self, entity_xml_id):
        entity = Entity.objects.get(xml_id=entity_xml_id)
        entity.deleted_by = self.__user
        entity.save()

        entity_version = self.get_entity_version_from_db(entity_xml_id)
        self.__mark_entity_properties_to_delete(entity_version)

        certainties = Certainty.objects.filter(
            file_version=self.__file.file_versions.order_by('-number')[0],
            target_xml_id=entity_xml_id
        )

        for certainty in certainties:
            certainty.deleted_by = self.__user

        Certainty.objects.bulk_update(certainties, ['deleted_by'])

    def mark_entity_property_to_delete(self, entity_xml_id, entity_property_name):
        entity_version = self.get_entity_version_from_db(entity_xml_id)

        self.__mark_entity_properties_to_delete(entity_version, [entity_property_name])

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
    def get_entity_from_db(entity_xml_id):
        entity = Entity.objects.get(xml_id=entity_xml_id)

        return entity

    @staticmethod
    def get_entity_version_from_db(entity_xml_id):
        entity_version_objects = EntityVersion.objects.filter(
            entity__xml_id=entity_xml_id,
            file_version__isnull=False
        ).order_by('-file_version')

        if not entity_version_objects:
            entity_version_objects = EntityVersion.objects.filter(
                entity__xml_id=entity_xml_id,
                file_version__isnull=True
            ).order_by('-id')

        entity_version_object = entity_version_objects[0]

        return entity_version_object

    def get_entity_property_from_db(self, entity_xml_id, entity_name):
        entity_version = self.get_entity_version_from_db(entity_xml_id)

        entity_property = EntityProperty.objects.get(
            entity_version=entity_version,
            name=entity_name
        )

        return entity_property
