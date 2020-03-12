from lxml import etree

from django.contrib.auth.models import User

from apps.api_vis.models import Entity, EntityProperty, EntityVersion
from apps.files_management.models import File, FileVersion
from apps.projects.models import EntitySchema

from django.conf import settings

from apps.api_vis.enums import TypeChoice


class Extractor:
    def __init__(self):
        self.__namespaces = settings.XML_NAMESPACES
        self.__xml_id_key = f"{{{self.__namespaces['xml']}}}id"

        self.__old_xml_content = ''
        self.__new_xml_content = ''

        self.__tree = None

        self.__listable_entities = []
        self.__unlistable_entities = []
        self.__custom_entities = []

        self.__is_changed = False

        self.__file = None
        self.__file_version = None

    def move_elements_to_db(self, xml_content, file_id):
        self.__old_xml_content = xml_content

        self.__load_file_metadata(file_id)
        self.__load_entities_schemes(file_id)

        self.__create_tree()
        self.__move_listable_entities()
        self.__copy_unlistable_entities()

        self.__create_xml_content()

        self.__check_if_changed()

        return self.__new_xml_content, self.__is_changed

    def __load_file_metadata(self, file_id):
        self.__file = File.objects.get(id=file_id)
        self.__file_version = FileVersion.objects.get(file=self.__file)

    def __load_entities_schemes(self, file_id):
        entities_schemes = self._get_entities_schemes_from_db(file_id)

        default_entities_names = settings.ENTITIES.keys()

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                self.__custom_entities.append(entity)
            else:
                if settings.ENTITIES[entity.name]['listable']:
                    self.__listable_entities.append(entity)
                else:
                    self.__unlistable_entities.append(entity)

    @staticmethod
    def _get_entities_schemes_from_db(file_id):
        file = File.objects.get(id=file_id)
        entities_schemes = EntitySchema.objects.filter(taxonomy__project_id=file.project.id)

        return entities_schemes

    def __create_tree(self):
        parser = etree.XMLParser(remove_blank_text=True)

        self.__tree = etree.fromstring(self.__old_xml_content, parser=parser)

    def __move_listable_entities(self):
        for entity in self.__listable_entities:
            list_tag = settings.ENTITIES[entity.name]['list_tag']
            xpath = f'//default:{list_tag}[@type="{entity.name}List"]//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__create_entities_in_db(elements, entity.name)

            xpath = f'//default:{list_tag}[@type="{entity.name}List"]'
            lists = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__remove_list_from_tree(lists)

    def __copy_unlistable_entities(self):
        for entity in self.__unlistable_entities:
            xpath = f'//default:text//default:body//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__create_entities_in_db(elements, entity.name)

    def __create_entities_in_db(self, elements, entity_name):
        for element in elements:
            entity_object = self.__create_entity_object(element, entity_name)
            entity_version_object = self.__create_entity_version_object()
            self.__create_entity_properties_objects(element, entity_name, entity_object, entity_version_object)

    def __save_entity_objects(self, entity_object, entity_version_object):
        entity_object.save()
        entity_version_object.entity = entity_object
        entity_version_object.save()

    def __create_entity_property_object(self, property, property_value, entity_version_object, entity_name):
        entity_property_object = EntityProperty(
            entity_version=entity_version_object,
            name=property,
            type=settings.ENTITIES[entity_name]['properties'][property]['type'],
            created_by=User.objects.get(id=1),
            created_in_version=self.__file.version_number,
        )

        entity_property_object.set_value(property_value)

        return entity_property_object

    def __create_entity_properties_objects(self, element, entity_name, entity_object, entity_version_object):
        objects_saved = False
        property_objects = []

        for property in settings.ENTITIES[entity_name]['properties']:
            xpath = f"{settings.ENTITIES[entity_name]['properties'][property]['xpath']}"
            property_values = element.xpath(xpath, namespaces=self.__namespaces)

            if property_values:
                if not objects_saved:
                    self.__save_entity_objects(entity_object, entity_version_object)
                    objects_saved = True

                entity_property_object = self.__create_entity_property_object(property, property_values[0],
                                                                              entity_version_object, entity_name)

                property_objects.append(entity_property_object)

        if property_objects:
            EntityProperty.objects.bulk_create(property_objects)

    def __remove_list_from_tree(self, lists):
        for list in lists:
            list.getparent().remove(list)

    def __create_entity_object(self, element, entity_name):
        entity_object = Entity(
            project=self.__file.project,
            file=self.__file,
            xml_id=element.attrib[self.__xml_id_key],
            created_by=User.objects.get(id=1),
            created_in_version=self.__file.version_number,
            type=entity_name,
        )

        return entity_object

    def __create_entity_version_object(self):
        entity_version_object = EntityVersion(
            fileversion=self.__file_version
        )

        return entity_version_object

    def __create_xml_content(self):
        self.__new_xml_content = etree.tounicode(self.__tree, pretty_print=True)

    def __check_if_changed(self):
        if self.__old_xml_content != self.__new_xml_content:
            self.__is_changed = True
