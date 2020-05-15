import json
import logging

from itertools import chain
from lxml import etree

from django.contrib.auth.models import User
from django.db.models import Q

from apps.api_vis.models import Certainty, EntityProperty, EntityVersion
from apps.close_reading.models import AnnotatingBodyContent
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match
from apps.files_management.models import File
from apps.projects.models import EntitySchema


from collaborative_platform.settings import DEFAULT_ENTITIES, XML_NAMESPACES


logger = logging.getLogger('annotator')


class ResponseGenerator:
    def __init__(self, file_id):
        self.__file = None
        self.__annotating_body_content = None

        self.__get_file_from_db(file_id)
        self.__load_body_content()

    def __get_file_from_db(self, file_id):
        self.__file = File.objects.get(id=file_id, deleted=False)

    def __load_body_content(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        try:
            self.__annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

        except AnnotatingBodyContent.DoesNotExist:
            file_version = self.__file.file_versions.order_by('-number')[0]
            xml_content = file_version.get_raw_content()
            body_content = self.__get_body_content(xml_content)

            self.__annotating_body_content = AnnotatingBodyContent.objects.create(file_symbol=room_name,
                                                                                  file_name=file_version.file.name,
                                                                                  body_content=body_content)

            logger.info(f"Load content of file: '{file_version.file.name}' in version: {file_version.number} "
                        f"to room: '{room_name}'")

    @staticmethod
    def __get_body_content(xml_content):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(xml_content, parser=parser)

        body_xpath = './default:text/default:body'
        body_element = get_first_xpath_match(tree, body_xpath, XML_NAMESPACES)

        body_content = etree.tounicode(body_element, pretty_print=True)

        return body_content

    def get_response(self):
        authors = self.__get_authors()
        certainties = self.__get_certainties()
        entities_lists = self.__get_entities_lists()

        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        response = {
            'status': 200,
            'message': 'OK',
            'authors': authors,
            'certainties': certainties,
            'entities_lists': entities_lists,
            'body_content': body_content,
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
        ).order_by('id')

        return authors

    def __get_authors_ids(self):
        entities_versions = EntityVersion.objects.filter(
            file_version=self.__file.file_versions.order_by('-number')[0]
        )

        entities_authors_ids = entities_versions.values_list('entity__created_by', flat=True)

        cetainties = Certainty.objects.filter(
            file_version=self.__file.file_versions.order_by('-number')[0]
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
                'xml:id': author.profile.get_xml_id(),
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
        certainties_saved = Certainty.objects.filter(
            file_version=self.__file.file_versions.order_by('-number')[0],
            created_in_file_version__isnull=False
        ).order_by('id')

        certainties_unsaved = Certainty.objects.filter(
            file=self.__file,
            created_in_file_version__isnull=True
        ).order_by('id')

        certainties = list(chain(certainties_saved, certainties_unsaved))

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
                'resp': f'#{certainty.created_by.profile.get_xml_id()}',
                'match': certainty.target_match,
                'target': f'#{certainty.target_xml_id}',
                'xml:id': certainty.xml_id,
                'assertedValue': certainty.asserted_value,
                'desc': certainty.description,
                'saved': True if certainty.created_in_file_version is not None else False,
                'deleted': True if certainty.deleted_by is not None else False
            }

            certainties_serialized.append(certainty_serialized)

        return certainties_serialized

    def __get_entities_lists(self):
        file_version = self.__file.file_versions.order_by('-number')[0]

        listable_entities_types = get_listable_entities_types(file_version.file.project)

        entities_lists = {}

        for entity_type in listable_entities_types:
            entities_list = self.__get_list_of_certain_type_entities(entity_type, file_version)

            entities_lists.update({entity_type: entities_list})

        return entities_lists

    def __get_list_of_certain_type_entities(self, entity_type, file_version):
        entities_versions = EntityVersion.objects.filter(
            Q(file_version=file_version) | Q(file_version__isnull=True),
            entity__type=entity_type,
        ).order_by('id')

        entities_list = []

        for entity_version in entities_versions:
            entity = {
                'type': entity_version.entity.type,
                'xml:id': entity_version.entity.xml_id,
                'resp': f'#{entity_version.entity.created_by.profile.get_xml_id()}',
                'saved': True if entity_version.file_version is not None else False,
                'deleted': True if entity_version.entity.deleted_by is not None else False
            }

            properties = self.__get_entity_properties(entity_version)

            entity.update({'properties': properties})

            entities_list.append(entity)

        return entities_list

    @staticmethod
    def __get_entity_properties(entity_version):
        entity_properties = EntityProperty.objects.filter(
            entity_version=entity_version
        ).order_by('name', 'created_in_file_version', 'deleted_by')

        properties = []

        for entity_property in entity_properties:
            property = {
                'name': entity_property.name,
                'value': entity_property.get_value(as_str=True),
                'saved': True if entity_property.created_in_file_version is not None else False,
                'deleted': True if entity_property.deleted_by is not None else False
            }

            properties.append(property)

        return properties

    def remove_xml_content(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        try:
            AnnotatingBodyContent.objects.get(file_symbol=room_name).delete()

            logger.info(f"Remove file content from room: '{room_name}'")
        except AnnotatingBodyContent.DoesNotExist:
            pass


def get_listable_entities_types(project):
    entities_schemes = EntitySchema.objects.filter(taxonomy__project=project).order_by('id')
    default_entities_names = DEFAULT_ENTITIES.keys()
    listable_entities_types = []

    for entity in entities_schemes:
        if entity.name not in default_entities_names:
            listable_entities_types.append(entity.name)
        elif DEFAULT_ENTITIES[entity.name]['listable']:
            listable_entities_types.append(entity.name)

    listable_entities_types = sorted(listable_entities_types)

    return listable_entities_types


def get_unlistable_entities_types(project):
    entities_schemes = EntitySchema.objects.filter(taxonomy__project=project).order_by('id')
    default_entities_names = DEFAULT_ENTITIES.keys()
    unlistable_entities_types = []

    for entity in entities_schemes:
        if entity.name in default_entities_names and not DEFAULT_ENTITIES[entity.name]['listable']:
            unlistable_entities_types.append(entity.name)

    unlistable_entities_types = sorted(unlistable_entities_types)

    return unlistable_entities_types


def get_custom_entities_types(project):
    entities_schemes = EntitySchema.objects.filter(taxonomy__project=project).order_by('id')
    default_entities_names = DEFAULT_ENTITIES.keys()
    custom_entities_types = []

    for entity in entities_schemes:
        if entity.name not in default_entities_names:
            custom_entities_types.append(entity.name)

    return custom_entities_types
