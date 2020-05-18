from apps.api_vis.models import Entity, EntityProperty, EntityVersion
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
