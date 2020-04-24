import json
import logging

from django.contrib.auth.models import User

from apps.api_vis.models import Certainty, EntityProperty, EntityVersion
from apps.close_reading.models import AnnotatingXmlContent
from apps.files_management.models import File
from apps.projects.models import EntitySchema


from collaborative_platform.settings import DEFAULT_ENTITIES


logger = logging.getLogger('annotator')


class ResponseGenerator:
    def __init__(self, file_id):
        self.__file = None
        self.__annotating_xml_content = None

        self.__get_file_from_db(file_id)
        self.__load_xml_content()

    def __get_file_from_db(self, file_id):
        self.__file = File.objects.get(id=file_id, deleted=False)

    def __load_xml_content(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        try:
            self.__annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_name)

        except AnnotatingXmlContent.DoesNotExist:
            file_version = self.__file.file_versions.last()

            xml_content = file_version.get_raw_content()

            # TODO: send only content of <body> element instead whole file

            self.__annotating_xml_content = AnnotatingXmlContent(file_symbol=room_name,
                                                                 file_name=file_version.file.name,
                                                                 xml_content=xml_content)
            self.__annotating_xml_content.save()

            logger.info(f"Load content of file: '{file_version.file.name}' in version: {file_version.number} "
                        f"to room: '{room_name}'")

    def get_response(self):
        authors = self.__get_authors()
        certainties = self.__get_certainties()
        entities_lists = self.__get_entities_lists()
        xml_content = self.__annotating_xml_content.xml_content

        response = {
            'status': 200,
            'message': 'OK',
            'authors': authors,
            'certainties': certainties,
            'entities_lists': entities_lists,
            'xml_content': xml_content,
        }

        response = json.dumps(response)

        return response

    def __get_authors(self):
        authors = self.__get_authors_from_db()
        authors = self.__serialize_authors(authors)

        return authors

    def __get_authors_from_db(self):
        authors_ids = self.__get_authors_ids()

        authors = User.objects.filter(
            id__in=authors_ids
        )

        return authors

    def __get_authors_ids(self):
        entities_versions = EntityVersion.objects.filter(
            file_version=self.__file.file_versions.last()
        )

        entities_authors_ids = entities_versions.values_list('entity__created_by', flat=True)

        cetainties = Certainty.objects.filter(
            file_version=self.__file.file_versions.last()
        )

        certainties_authors_ids = cetainties.values_list('created_by', flat=True)

        authors_ids = set()
        authors_ids.update(entities_authors_ids)
        authors_ids.update(certainties_authors_ids)

        return authors_ids

    @staticmethod
    def __serialize_authors(authors):
        serialized_authors = []

        for author in authors:
            serialized_author = {
                'id': author.id,
                'forename': author.first_name,
                'surname': author.last_name,
                'username': author.username,
            }

            serialized_authors.append(serialized_author)

        return serialized_authors

    def __get_certainties(self):
        certainties = self.__get_certainties_from_db()
        certainties = self.__serialize_certainties(certainties)

        # TODO: Append certainties created from unifications

        return certainties

    def __get_certainties_from_db(self):
        certainties = Certainty.objects.filter(
            file_version=self.__file.file_versions.last(),
        )

        return certainties

    @staticmethod
    def __serialize_certainties(certainties):
        certainties_serialized = []

        for certainty in certainties:
            certainty_serialized = {
                'ana': certainty.get_categories(as_str=True),
                'locus': certainty.locus,
                'degree': certainty.degree,
                'cert': certainty.cert,
                'resp': certainty.created_by.username,
                'match': certainty.target_match,
                'target': certainty.target_xml_id,
                'xml:id': certainty.xml_id,
                'assertedValue': certainty.asserted_value,
                'desc': certainty.description,
            }

            certainties_serialized.append(certainty_serialized)

        return certainties_serialized

    def __get_entities_lists(self):
        file_version = self.__file.file_versions.last()

        listable_entities_types = self.__get_entities_types_for_lists(file_version)

        entities_lists = {}

        for entity_type in listable_entities_types:
            entities_list = self.__get_list_of_certain_type_entities(entity_type, file_version)

            entities_lists.update({entity_type: entities_list})

        return entities_lists

    @staticmethod
    def __get_entities_types_for_lists(file_version):
        entities_schemes = EntitySchema.objects.filter(taxonomy__project=file_version.file.project)
        default_entities_names = DEFAULT_ENTITIES.keys()
        listable_entities_types = []

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                listable_entities_types.append(entity.name)
            elif DEFAULT_ENTITIES[entity.name]['listable']:
                listable_entities_types.append(entity.name)

        return listable_entities_types

    def __get_list_of_certain_type_entities(self, entity_type, file_version):
        entities_versions = EntityVersion.objects.filter(
            entity__type=entity_type,
            file_version=file_version,
        )

        entities_list = []

        for entity_version in entities_versions:
            entity = {
                'type': entity_version.entity.type,
                'xml:id': entity_version.entity.xml_id,
                'resp': entity_version.entity.created_by.username,
            }

            properties = self.__get_entity_properties(entity_version)

            entity.update({'properties': properties})

            entities_list.append(entity)

        return entities_list

    @staticmethod
    def __get_entity_properties(entity_version):
        entity_properties = EntityProperty.objects.filter(
            entity_version=entity_version
        )

        properties = {entity_property.name: entity_property.get_value(as_str=True) for entity_property in
                      entity_properties}

        return properties

    def remove_xml_content(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        try:
            AnnotatingXmlContent.objects.get(file_symbol=room_name).delete()

            logger.info(f"Remove file content from room: '{room_name}'")
        except AnnotatingXmlContent.DoesNotExist:
            pass
