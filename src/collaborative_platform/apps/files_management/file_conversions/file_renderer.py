import re

from lxml import etree

from apps.files_management.helpers import append_unifications
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match
from apps.api_vis.models import Entity, EntityVersion, EntityProperty
from apps.projects.models import EntitySchema

from collaborative_platform.settings import XML_NAMESPACES, DEFAULT_ENTITIES, NS_MAP, CUSTOM_ENTITY


class FileRenderer:
    def __init__(self):
        self.__file_version = None

        self.__tree = None

        self.__listable_entities = []
        self.__custom_entities = []

    def render_file_version(self, file_version):
        self.__file_version = file_version

        self.__load_entities_schemes()

        self.__create_tree()
        self.__append_listable_entities()
        self.__append_custom_entities()



















        # TODO: Append custom entities



        # TODO: Append certainties



        # TODO: Append annotators



        # xml_content = append_unifications(xml_content, file_version)

        xml_content = self.__create_xml_content()

        return xml_content

    def __create_tree(self):
        raw_content = self.__file_version.get_raw_content()

        parser = etree.XMLParser(remove_blank_text=True)
        self.__tree = etree.fromstring(raw_content, parser=parser)

    def __load_entities_schemes(self):
        entities_schemes = self.__get_entities_schemes_from_db()

        default_entities_names = DEFAULT_ENTITIES.keys()

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                self.__custom_entities.append(entity)
            elif DEFAULT_ENTITIES[entity.name]['listable']:
                self.__listable_entities.append(entity)

    def __get_entities_schemes_from_db(self):
        entities_schemes = EntitySchema.objects.filter(taxonomy__project=self.__file_version.file.project)

        return entities_schemes

    def __append_listable_entities(self):
        for entity in self.__listable_entities:
            entities_versions = self.__get_entities_versions_from_db(entity.name)
            elements = self.__create_entities_elements(entities_versions)

            list_tag = DEFAULT_ENTITIES[entity.name]['list_tag']

            if entity.body_list:
                list_xpath = f'/default:TEI/default:text/default:body/default:div[@type="{entity.name}"]/' \
                             f'default:{list_tag}[@type="{entity.name}List"]'
            else:
                list_xpath = f'/default:TEI/default:teiHeader/default:sourceDesc/' \
                             f'default:{list_tag}[@type="{entity.name}List"]'

            self.__append_elements_to_the_list(elements, list_xpath)

    def __append_custom_entities(self):
        for entity in self.__custom_entities:
            entities_versions = self.__get_entities_versions_from_db(entity.name)
            elements = self.__create_entities_elements(entities_versions, custom=True)

            if entity.body_list:
                list_xpath = f'/default:TEI/default:text/default:body/default:div[@type="{entity.name}"]/' \
                             f'default:listObject[@type="{entity.name}List"]'
            else:
                list_xpath = f'/default:TEI/default:teiHeader/default:sourceDesc/' \
                             f'default:listObject[@type="{entity.name}List"]'

            self.__append_elements_to_the_list(elements, list_xpath)

    def __get_entities_versions_from_db(self, entity_type):
        entities_versions = EntityVersion.objects.filter(
            file_version=self.__file_version,
            entity__type=entity_type,
        )

        return entities_versions

    def __create_entities_elements(self, entities_versions, custom=False):
        elements = []

        for entity_version in entities_versions:
            entity_element = self.__create_entity_element(entity_version, custom)

            self.__append_entity_properties(entity_element, entity_version, custom)

            elements.append(entity_element)

        return elements

    def __create_entity_element(self, entity_version, custom=False):
        default_prefix = '{%s}' % XML_NAMESPACES['default']
        xml_prefix = '{%s}' % XML_NAMESPACES['xml']

        if not custom:
            entity_element = etree.Element(default_prefix + entity_version.entity.type, nsmap=NS_MAP)
        else:
            entity_element = etree.Element(default_prefix + 'object', nsmap=NS_MAP)
            entity_element.set('type', entity_version.entity.type)

        entity_element.set(xml_prefix + 'id', entity_version.entity.xml_id)
        entity_element.set('resp', str(entity_version.entity.created_by_id))

        return entity_element

    def __append_entity_properties(self, entity_element, entity_version, custom=False):
        entities_properties = EntityProperty.objects.filter(
            entity_version=entity_version
        )

        if not custom:
            properties = DEFAULT_ENTITIES[entity_version.entity.type]['properties']
        else:
            properties = CUSTOM_ENTITY['properties']

        for entity_property in entities_properties:
            xpath = properties[entity_property.name]['xpath']
            value = entity_property.get_value(as_str=True)

            add_property(entity_element, xpath, value)

    def __append_elements_to_the_list(self, elements, list_xpath):
        list = get_first_xpath_match(self.__tree, list_xpath, XML_NAMESPACES)

        if not list:
            tree = create_elements_from_xpath(self.__tree, list_xpath)
            list = get_first_xpath_match(tree, list_xpath, XML_NAMESPACES)

        for element in elements:
            list.append(element)

    def __create_xml_content(self):
        xml_content = etree.tounicode(self.__tree, pretty_print=True)

        return xml_content











def add_property(parent, xpath, value):
    xpath = xpath.replace('./', '')
    splitted_xpath = xpath.split('/', 1)

    if len(splitted_xpath) == 1:
        target = splitted_xpath[0]

        if '@' in target:
            key = target.replace('@', '')
            parent.set(key, value)

        elif 'text()' in target:
            parent.text = value

        else:
            raise ValueError("Xpath for this property not pointing to attribute(@) or text (text())")

    elif len(splitted_xpath) > 1:
        child_name = splitted_xpath[0]
        child_xpath = f'./{child_name}'
        child = get_first_xpath_match(parent, child_xpath, XML_NAMESPACES)

        if not child:
            prefix = child_name.split(':')[0]
            prefix = '{%s}' % XML_NAMESPACES[prefix]
            name = child_name.split(':')[1]

            child = etree.Element(prefix + name, nsmap=NS_MAP)
            parent.append(child)

        return add_property(child, splitted_xpath[1], value)



def create_elements_from_xpath(tree, xpath):
    default_namespace = XML_NAMESPACES['default']

    ns_map = {
        None: default_namespace
    }

    path_steps = xpath.split('/')
    path_steps = [step for step in path_steps if step != '']

    for i in range(len(path_steps)):
        i += 1

        element_xpath = '/' + '/'.join(path_steps[:i])
        element = tree.xpath(element_xpath, namespaces=XML_NAMESPACES)

        if not element:
            parent_xpath = '/' + '/'.join(path_steps[:i - 1])
            parent = tree.xpath(parent_xpath, namespaces=XML_NAMESPACES)

            step = path_steps[i - 1]

            attributes_regex = r'\[.*?\]'
            attributes_dict = {}
            match = re.search(attributes_regex, step)

            if match:
                attributes_part = match.group()
                step = step.replace(attributes_part, '')

                attribute_regex = r'@\w*?=[\'"].*?[\'"]'
                attributes = re.findall(attribute_regex, attributes_part)

                for attribute in attributes:
                    key = attribute.split('=')[0]
                    key = key.replace('@', '')

                    value = attribute.split('=')[1]
                    value = re.sub(r'[\'"]', '', value)

                    attributes_dict.update({key: value})

            if ':' in step:
                prefix = step.split(':')[0]
                name = step.split(':')[1]

            else:
                prefix = ''
                name = step

            namespace = '{%s}' % XML_NAMESPACES[prefix]

            element = etree.Element(namespace + name, nsmap=ns_map)

            if attributes_dict:
                for key, value in attributes_dict.items():
                    element.set(key, value)

            parent[0].append(element)

    return tree
