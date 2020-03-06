from lxml import etree

from django.conf import settings

from apps.projects.models import EntitySchema


class IDsCorrector:
    def __init__(self):
        self.__namespaces = settings.XML_NAMESPACES
        self.__xml_id_key = f"{{{self.__namespaces['xml']}}}id"

        self.__tree = None

        self.__listable_entities = []
        self.__unlistable_entities = []
        self.__custom_entities = []

        self.__max_xml_ids = {}

    def correct_ids(self, xml_content, project_id):
        self.__load_entities_schemes(project_id)
        self.__initiate_max_xml_ids()

        self.__create_tree(xml_content)

        self.__correct_collision_xml_ids()
        self.__correct_listable_entities_ids()
        self.__correct_unlistable_entities_ids()
        self.__correct_custom_entities_ids()
        self.__correct_tags_ids_in_body_text_related_to_entities()
        self.__correct_certainties_xml_ids()

        xml_content = self.__create_xml_content()

        return xml_content

    def __load_entities_schemes(self, project_id):
        entities_schemes = self._get_entities_schemes_from_db(project_id)

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
    def _get_entities_schemes_from_db(project_id):
        entities_schemes = EntitySchema.objects.filter(taxonomy__project_id=project_id)

        return entities_schemes

    def __initiate_max_xml_ids(self):
        usable_tags = self.__get_usable_tags()

        for tag_name in usable_tags:
            self.__max_xml_ids.update({tag_name: 0})

    def __get_usable_tags(self):
        entities = self.__listable_entities + self.__unlistable_entities + self.__custom_entities
        default_entities_names = settings.ENTITIES.keys()

        usable_tags = []

        for entity in entities:
            usable_tags.append(entity.name)

            if entity.name in default_entities_names:
                entity_text_tag = settings.ENTITIES[entity.name]['text_tag']
                usable_tags.append(entity_text_tag)

        usable_tags += settings.ADDITIONAL_USABLE_TAGS
        usable_tags = set(usable_tags)

        return usable_tags

    def __create_tree(self, xml_content):
        parser = etree.XMLParser(remove_blank_text=True)

        self.__tree = etree.fromstring(xml_content, parser=parser)

    def __correct_collision_xml_ids(self):
        usable_tags = self.__get_usable_tags()

        for tag_name in usable_tags:
            xpath = f"//*[contains(@xml:id, '{tag_name}-')]"
            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__correct_elements_ids(elements, tag_name, collision=True)

    def __correct_listable_entities_ids(self):
        for entity in self.__listable_entities:
            list_tag = settings.ENTITIES[entity.name]['list_tag']
            xpath = f'//default:{list_tag}[@type="{entity.name}List"]//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__correct_elements_ids(elements, entity.name)

    def __correct_unlistable_entities_ids(self):
        for entity in self.__unlistable_entities:
            xpath = f'//default:text//default:body//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__correct_elements_ids(elements, entity.name)

    def __correct_custom_entities_ids(self):
        for entity in self.__custom_entities:
            xpath = f'//default:listObject[@type="{entity.name}List"]//default:object[@type="{entity.name}"]'
            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            self.__correct_elements_ids(elements, entity.name)

    def __correct_tags_ids_in_body_text_related_to_entities(self):
        for entity in self.__listable_entities:
            list_tag = settings.ENTITIES[entity.name]['list_tag']
            text_tag = settings.ENTITIES[entity.name]['text_tag']

            xpath_body = f'//default:text//default:body//default:{text_tag}'
            xpath_list = f'//default:{list_tag}[@type="{entity.name}List"]//default:{text_tag}'

            elements = self.__get_difference_of_elements(xpath_body, xpath_list)

            self.__correct_elements_ids(elements, text_tag)

        xpath_body = f'//default:text//default:body//default:objectName'
        xpath_list = f'//default:listObject//default:objectName'

        elements = self.__get_difference_of_elements(xpath_body, xpath_list)

        self.__correct_elements_ids(elements, 'objectName')

    def __correct_certainties_xml_ids(self):
        xpath = f'//default:teiHeader//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]' \
                f'//default:certainty'
        elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

        self.__correct_elements_ids(elements, 'certainty')

    def __correct_elements_ids(self, elements, entity_name, collision=False):
        for element in elements:
            if self.__xml_id_key in element.attrib:
                self.__update_element_xml_id_and_references(element, entity_name, collision)

            else:
                self.__update_element_xml_id(element, entity_name)

    def __get_difference_of_elements(self, xpath_a, xpath_b):
        elements_a = self.__tree.xpath(xpath_a, namespaces=self.__namespaces)
        elements_b = self.__tree.xpath(xpath_b, namespaces=self.__namespaces)

        elements = set(elements_a) - set(elements_b)
        elements = list(elements)
        elements = sorted(elements, key=lambda element: str(element.sourceline) + element.text + element.tail)

        return elements

    def __update_element_xml_id_and_references(self, element, entity_name, collision=False):
        old_xml_id = element.attrib[self.__xml_id_key]
        new_xml_id = self.__update_element_xml_id(element, entity_name, collision=collision)

        reference_attributes = ['ref', 'target']

        for attribute in reference_attributes:
            xpath = f"//*[contains(concat(' ', @{attribute}, ' '), ' #{old_xml_id} ')]"

            elements = self.__tree.xpath(xpath, namespaces=self.__namespaces)

            for element in elements:
                self.__update_element_attribute(element, attribute, old_xml_id, new_xml_id)

    def __update_element_xml_id(self, element, entity_name, collision=False):
        if not collision:
            xml_id_number = self.__get_next_xml_id_number(entity_name)
            new_xml_id = f'{entity_name}-{xml_id_number}'
        else:
            old_xml_id = element.attrib[self.__xml_id_key]
            old_xml_id = old_xml_id.replace('-', '_')
            new_xml_id = f'old_{old_xml_id}'

        element.attrib[self.__xml_id_key] = new_xml_id

        return new_xml_id

    def __get_next_xml_id_number(self, entity_name):
        xml_id_number = self.__max_xml_ids[entity_name]

        self.__max_xml_ids[entity_name] += 1

        return xml_id_number

    def __update_element_attribute(self, element, attribute, old_value, new_value):
        old_reference = element.attrib[attribute]
        new_reference = old_reference.replace(f'#{old_value}', f'#{new_value}')
        element.attrib[attribute] = new_reference

    def __create_xml_content(self):
        xml_content = etree.tounicode(self.__tree, pretty_print=True)

        return xml_content
