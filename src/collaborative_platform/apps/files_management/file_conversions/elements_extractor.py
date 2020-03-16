from lxml import etree

from django.contrib.auth.models import User

from collaborative_platform.settings import CUSTOM_ENTITY, DEFAULT_ENTITIES, XML_NAMESPACES

from apps.api_vis.models import Entity, EntityProperty, EntityVersion
from apps.core.models import VirtualUser
from apps.files_management.models import File, FileVersion
from apps.projects.models import EntitySchema


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class ElementsExtractor:
    def __init__(self):
        self.__old_xml_content = ''
        self.__new_xml_content = ''

        self.__tree = None

        self.__listable_entities = []
        self.__unlistable_entities = []
        self.__custom_entities = []

        self.__is_changed = False

        self.__file = None
        self.__file_version = None
        self.__message = ''

    def move_elements_to_db(self, xml_content, file_id):
        self.__old_xml_content = xml_content

        self.__load_file_objects(file_id)
        self.__load_entities_schemes()

        self.__create_tree()
        self.__move_listable_entities()
        self.__copy_unlistable_entities()
        self.__move_custom_entities()
        self.__extract_annotators()
        self.__create_xml_content()

        self.__check_if_changed()

        return self.__new_xml_content, self.__is_changed, self.__message

    def __load_file_objects(self, file_id):
        self.__file = File.objects.get(id=file_id)
        self.__file_version = FileVersion.objects.get(file=self.__file)

    def __load_entities_schemes(self):
        entities_schemes = self._get_entities_schemes_from_db()

        default_entities_names = DEFAULT_ENTITIES.keys()

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                self.__custom_entities.append(entity)
            else:
                if DEFAULT_ENTITIES[entity.name]['listable']:
                    self.__listable_entities.append(entity)
                else:
                    self.__unlistable_entities.append(entity)

    def _get_entities_schemes_from_db(self):
        entities_schemes = EntitySchema.objects.filter(taxonomy__project_id=self.__file.project.id)

        return entities_schemes

    def __create_tree(self):
        parser = etree.XMLParser(remove_blank_text=True)

        self.__tree = etree.fromstring(self.__old_xml_content, parser=parser)

    def __move_listable_entities(self):
        for entity in self.__listable_entities:
            list_tag = DEFAULT_ENTITIES[entity.name]['list_tag']
            xpath = f'//default:{list_tag}[@type="{entity.name}List"]//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__create_entities_in_db(elements, entity.name)

            xpath = f'//default:{list_tag}[@type="{entity.name}List"]'
            lists = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__remove_elements_from_tree(lists)

    def __copy_unlistable_entities(self):
        for entity in self.__unlistable_entities:
            xpath = f'//default:text//default:body//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__create_entities_in_db(elements, entity.name)

    def __move_custom_entities(self):
        for entity in self.__custom_entities:
            xpath = f'//default:listObject[@type="{entity.name}List"]//default:object[@type="{entity.name}"]'
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__create_entities_in_db(elements, entity.name, custom=True)

            xpath = f'//default:listObject[@type="{entity.name}List"]'
            lists = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__remove_elements_from_tree(lists)

    def __extract_annotators(self):
        annotators_map = {}

        xpath = '//default:teiHeader//default:profileDesc//default:particDesc' \
                '//default:listPerson[@type="PROVIDEDH Annotators"]/default:person'
        elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

        for element in elements:
            email = self.__get_first_xpath_match(element, './/default:email/text()', XML_NAMESPACES)
            forename = self.__get_first_xpath_match(element, './/default:forename/text()', XML_NAMESPACES)
            surname = self.__get_first_xpath_match(element, './/default:surname/text()', XML_NAMESPACES)
            xml_id = self.__get_first_xpath_match(element, '@xml:id', XML_NAMESPACES)

            user = self.__get_user(forename, surname, email)

            annotators_map.update({xml_id: user})

        xpath = '//default:teiHeader//default:profileDesc//default:particDesc' \
                '//default:listPerson[@type="PROVIDEDH Annotators"]'
        lists = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

        self.__remove_elements_from_tree(lists)

        return annotators_map

    def __create_entities_in_db(self, elements, entity_name, custom=False):
        for element in elements:
            entity_object = self.__create_entity_object(element, entity_name)
            entity_version_object = self.__create_entity_version_object()
            self.__create_entity_properties_objects(element, entity_name, entity_object, entity_version_object, custom)

    def __create_entity_object(self, element, entity_name):
        entity_object = Entity(
            project=self.__file.project,
            file=self.__file,
            xml_id=element.attrib[XML_ID_KEY],
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

    def __create_entity_properties_objects(self, element, entity_name, entity_object, entity_version_object,
                                           custom=False):
        objects_saved = False
        property_objects = []

        if not custom:
            properties = DEFAULT_ENTITIES[entity_name]['properties']
        else:
            properties = CUSTOM_ENTITY['properties']

        for property in properties:
            xpath = f"{properties[property]['xpath']}"
            property_values = element.xpath(xpath, namespaces=XML_NAMESPACES)
            property_type = properties[property]['type']

            if property_values:
                if not objects_saved:
                    self.__save_entity_objects(entity_object, entity_version_object)
                    objects_saved = True

                entity_property_object = self.__create_entity_property_object(property, property_type,
                                                                              property_values[0], entity_version_object)

                property_objects.append(entity_property_object)

        if property_objects:
            EntityProperty.objects.bulk_create(property_objects)

    def __save_entity_objects(self, entity_object, entity_version_object):
        entity_object.save()
        entity_version_object.entity = entity_object
        entity_version_object.save()

    def __create_entity_property_object(self, property, property_type, property_value, entity_version_object):
        entity_property_object = EntityProperty(
            entity_version=entity_version_object,
            name=property,
            type=property_type,
            created_by=User.objects.get(id=1),
            created_in_version=self.__file.version_number,
        )

        entity_property_object.set_value(property_value)

        return entity_property_object

    @staticmethod
    def __get_first_xpath_match(root, xpath, namespaces):
        matches = root.xpath(xpath, namespaces=namespaces)

        if matches:
            match = matches[0]

            return match
        else:
            return None

    @staticmethod
    def __get_user(forename, surname, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                if email:
                    user = VirtualUser.objects.get(email=email)
                else:
                    user = VirtualUser.objects.get(first_name=forename, last_name=surname)
            except VirtualUser.DoesNotExist:
                user = VirtualUser(
                    first_name=forename,
                    last_name=surname,
                    email=email,
                )
        return user

    def __remove_elements_from_tree(self, elements):
        for element in elements:
            self.remove_element(element, clean_up_parent=True)

    def remove_element(self, element, clean_up_parent=False):
        parent = element.getparent()
        parent.remove(element)

        if len(parent) == 0 and clean_up_parent:
            self.remove_element(parent)

    def __create_xml_content(self):
        self.__new_xml_content = etree.tounicode(self.__tree, pretty_print=True)

    def __check_if_changed(self):
        if self.__old_xml_content != self.__new_xml_content:
            self.__is_changed = True

            self.__message = "Moved elements from file to database."
