from lxml import etree

from collaborative_platform.settings import ADDITIONAL_XML_ID_BASES, ADDITIONAL_USABLE_TAGS, DEFAULT_ENTITIES, \
    XML_NAMESPACES

from apps.files_management.models import File, FileMaxXmlIds
from apps.projects.models import EntitySchema


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class IDsCorrector:
    def __init__(self):
        self.__old_xml_content = ''
        self.__new_xml_content = ''

        self.__tree = None

        self.__listable_entities = []
        self.__unlistable_entities = []
        self.__custom_entities = []

        self.__max_xml_ids = {}

        self.__is_changed = False
        self.__message = ''

    def correct_ids(self, xml_content, file_id):
        self.__old_xml_content = xml_content

        self.__load_entities_schemes(file_id)
        self.__initiate_max_xml_ids()

        self.__create_tree()
        self.__correct_collision_xml_ids()
        self.__correct_listable_entities_ids()
        self.__correct_unlistable_entities_ids()
        self.__correct_custom_entities_ids()
        self.__correct_tags_ids_in_body_text_related_to_entities()
        self.__correct_annotators_ids()
        self.__correct_certainties_xml_ids()
        self.__create_xml_content()

        self._dump_max_xml_ids_to_db(file_id)

        self.__check_if_changed()

        return self.__new_xml_content, self.__is_changed, self.__message

    def __load_entities_schemes(self, file_id):
        entities_schemes = self._get_entities_schemes_from_db(file_id)

        default_entities_names = DEFAULT_ENTITIES.keys()

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                self.__custom_entities.append(entity)
            else:
                if DEFAULT_ENTITIES[entity.name]['listable']:
                    self.__listable_entities.append(entity)
                else:
                    self.__unlistable_entities.append(entity)

    @staticmethod
    def _get_entities_schemes_from_db(file_id):
        file = File.objects.get(id=file_id)
        entities_schemes = EntitySchema.objects.filter(taxonomy__project_id=file.project.id)

        return entities_schemes

    def __initiate_max_xml_ids(self):
        usable_tags = self.__get_usable_tags()

        xml_ids_bases = usable_tags | set(ADDITIONAL_XML_ID_BASES)

        for xml_id_base in xml_ids_bases:
            self.__max_xml_ids.update({xml_id_base: 0})

    def __get_usable_tags(self):
        entities = self.__listable_entities + self.__unlistable_entities + self.__custom_entities
        default_entities_names = DEFAULT_ENTITIES.keys()

        usable_tags = []

        for entity in entities:
            usable_tags.append(entity.name)

            if entity.name in default_entities_names:
                entity_text_tag = DEFAULT_ENTITIES[entity.name]['text_tag']
                usable_tags.append(entity_text_tag)

        usable_tags += ADDITIONAL_USABLE_TAGS
        usable_tags = set(usable_tags)

        return usable_tags

    def __create_tree(self):
        parser = etree.XMLParser(remove_blank_text=True)

        self.__tree = etree.fromstring(self.__old_xml_content, parser=parser)

    def __correct_collision_xml_ids(self):
        usable_tags = self.__get_usable_tags()

        for tag_name in usable_tags:
            xpath = f"//*[contains(@xml:id, '{tag_name}-')]"
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__correct_elements_ids(elements, tag_name, collision=True)

    def __correct_listable_entities_ids(self):
        for entity in self.__listable_entities:
            list_tag = DEFAULT_ENTITIES[entity.name]['list_tag']
            xpath = f'//default:{list_tag}[@type="{entity.name}List"]//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__correct_elements_ids(elements, entity.name)

    def __correct_unlistable_entities_ids(self):
        for entity in self.__unlistable_entities:
            xpath = f'//default:text//default:body//default:{entity.name}'
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__correct_elements_ids(elements, entity.name)

    def __correct_custom_entities_ids(self):
        for entity in self.__custom_entities:
            xpath = f'//default:listObject[@type="{entity.name}List"]//default:object[@type="{entity.name}"]'
            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            self.__correct_elements_ids(elements, entity.name)

    def __correct_tags_ids_in_body_text_related_to_entities(self):
        elements_on_lists = []

        for entity in self.__listable_entities:
            list_tag = DEFAULT_ENTITIES[entity.name]['list_tag']
            xpath_list = f'//default:{list_tag}[@type="{entity.name}List"]//default:name'
            elements = self.__tree.xpath(xpath_list, namespaces=XML_NAMESPACES)

            elements_on_lists.extend(elements)

        xpath_body = f'//default:text//default:body//default:name'
        elements_in_body = self.__tree.xpath(xpath_body, namespaces=XML_NAMESPACES)

        elements = self.__get_difference_of_elements(elements_in_body, elements_on_lists)

        self.__correct_elements_ids(elements, 'name')

    def __correct_annotators_ids(self):
        xpath = f'//default:teiHeader//default:profileDesc//default:particDesc//' \
                f'default:listPerson[@type="PROVIDEDH Annotators"]/default:person'

        elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

        self.__correct_elements_ids(elements, 'annotator')


    def __correct_certainties_xml_ids(self):
        xpath = f'//default:teiHeader//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]' \
                f'//default:certainty'
        elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

        self.__correct_elements_ids(elements, 'certainty')

    def __correct_elements_ids(self, elements, xml_id_base, collision=False):
        for element in elements:
            if XML_ID_KEY in element.attrib:
                self.__update_element_xml_id_and_references(element, xml_id_base, collision)

            else:
                self.__update_element_xml_id(element, xml_id_base)

    def __get_difference_of_elements(self, elements_a, elements_b):
        elements = set(elements_a) - set(elements_b)
        elements = list(elements)

        elements = sorted(elements, key=lambda element: str(element.sourceline) + (element.text or '')
                                                        + (element.tail or ''))

        return elements

    def __update_element_xml_id_and_references(self, element, xml_id_base, collision=False):
        old_xml_id = element.attrib[XML_ID_KEY]
        new_xml_id = self.__update_element_xml_id(element, xml_id_base, collision=collision)

        reference_attributes = ['ref', 'resp', 'target']

        for attribute in reference_attributes:
            xpath = f"//*[contains(concat(' ', @{attribute}, ' '), ' #{old_xml_id} ')]"

            elements = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)

            for element in elements:
                self.__update_element_attribute(element, attribute, old_xml_id, new_xml_id)

    def __update_element_xml_id(self, element, xml_id_base, collision=False):
        if not collision:
            xml_id_number = self.__get_next_xml_id_number(xml_id_base)
            new_xml_id = f'{xml_id_base}-{xml_id_number}'
        else:
            old_xml_id = element.attrib[XML_ID_KEY]
            old_xml_id = old_xml_id.replace('-', '_')
            new_xml_id = f'old_{old_xml_id}'

        element.attrib[XML_ID_KEY] = new_xml_id

        return new_xml_id

    def __get_next_xml_id_number(self, xml_id_base):
        xml_id_number = self.__max_xml_ids[xml_id_base]

        self.__max_xml_ids[xml_id_base] += 1

        return xml_id_number

    @staticmethod
    def __update_element_attribute(element, attribute, old_value, new_value):
        old_reference = element.attrib[attribute]
        new_reference = old_reference.replace(f'#{old_value}', f'#{new_value}')
        element.attrib[attribute] = new_reference

    def __create_xml_content(self):
        self.__new_xml_content = etree.tounicode(self.__tree, pretty_print=True)

    def _dump_max_xml_ids_to_db(self, file_id):
        for xml_id_base, xml_id_number in self.__max_xml_ids.items():
            FileMaxXmlIds.objects.create(
                file_id=file_id,
                xml_id_base=xml_id_base,
                xml_id_number=xml_id_number,
            )

    def __check_if_changed(self):
        if self.__old_xml_content != self.__new_xml_content:
            self.__is_changed = True

            self.__message = "Corrected xml:ids for project entities."
