import re

from lxml import etree

from apps.api_vis.models import EntityVersion
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match

from collaborative_platform.settings import XML_NAMESPACES


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class XmlHandler:
    def __init__(self, listable_entities_types, unlistable_entities_types, custom_entities_types):
        self.__listable_entities_types = listable_entities_types
        self.__unlistable_entities_types = unlistable_entities_types
        self.__custom_entities_types = custom_entities_types

    def add_new_tag_to_text(self, text, start_pos, end_pos, tag_xml_id, annotator_xml_id):
        text_result = self.__add_tag(text, start_pos, end_pos, tag_xml_id, annotator_xml_id)

        return text_result

    def mark_tag_to_delete(self, text, tag_xml_id, annotator_xml_id):
        attributes_to_add = {
            'deleted': 'true',
            'saved': 'false',
            'resp': f'#{annotator_xml_id}',
        }

        text_result = self.__update_tag_in_body(text, tag_xml_id, attributes_to_add=attributes_to_add)

        return text_result

    @staticmethod
    def __add_tag(text, start_pos, end_pos, tag_xml_id, annotator_xml_id):
        text_before = text[:start_pos]
        text_inside = text[start_pos:end_pos]
        text_after = text[end_pos:]

        text_result = f'{text_before}<ab xml:id="{tag_xml_id}" resp="#{annotator_xml_id}" ' \
                      f'saved="false">{text_inside}</ab>{text_after}'

        return text_result

    def __update_tag_in_body(self, text, tag_xml_id, new_tag=None, attributes_to_add=None, attributes_to_delete=None):
        tree = etree.fromstring(text)

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_xml_id} ')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if element is None:
            xpath = f"//*[contains(concat(' ', @newId, ' '), ' {tag_xml_id} ')]"
            element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if attributes_to_add:
            for attribute, value in sorted(attributes_to_add.items()):
                if new_tag in ['date', 'time'] and attribute == 'name':
                    continue

                if attribute in element.attrib:
                    old_values = element.attrib[attribute]
                    old_values = set(old_values.split(' '))

                    if value not in old_values:
                        old_values.add(value)
                        new_values = ' '.join(sorted(old_values))

                        element.set(attribute, new_values)

                else:
                    element.set(attribute, value)

        if attributes_to_delete:
            for attribute, value in attributes_to_delete.items():
                if attribute in element.attrib:
                    old_values = element.attrib[attribute]
                    old_values = set(old_values.split(' '))

                    if value in old_values:
                        old_values.remove(value)

                    if old_values:
                        new_values = ' '.join(sorted(old_values))
                        element.attrib[attribute] = new_values
                    else:
                        element.attrib.pop(attribute)

        references = element.attrib.get('ref')

        if references:
            references = set(references.split(' '))
        else:
            references = set()

        references_deleted = element.attrib.get('refDeleted')

        if references_deleted:
            references_deleted = set(references_deleted.split(' '))
        else:
            references_deleted = set()

        remaining_references = references - references_deleted

        if not remaining_references:
            tag_name = element.tag
            tag_name = re.sub(r'{.*?}', '', tag_name)

            if tag_name in self.__unlistable_entities_types:
                xml_id = element.attrib[XML_ID_KEY]

                # # TODO: Move handling database to DbHandler class
                # entity_version = EntityVersion.objects.filter(
                #     file_version=self.__file.file_versions.order_by('-id')[0],
                #     entity__xml_id=xml_id
                # )
                #
                # if not entity_version:
                #     prefix = "{%s}" % XML_NAMESPACES['default']
                #     tag = prefix + 'ab'
                #     element.tag = tag
                #
                # elif f'#{xml_id}' in references_deleted:
                #     prefix = "{%s}" % XML_NAMESPACES['default']
                #     tag = prefix + 'ab'
                #     element.tag = tag

                prefix = "{%s}" % XML_NAMESPACES['default']
                tag = prefix + 'ab'
                element.tag = tag

            else:
                prefix = "{%s}" % XML_NAMESPACES['default']
                tag = prefix + 'ab'
                element.tag = tag

        if new_tag:
            prefix = "{%s}" % XML_NAMESPACES['default']
            tag = prefix + new_tag
            element.tag = tag

        text_result = etree.tounicode(tree, pretty_print=True)

        return text_result

    def move_tag_to_new_position(self, text, start_pos, end_pos, tag_xml_id, annotator_xml_id):
        temp_xml_id = f'{tag_xml_id}-new'

        # Get tag name
        tree = etree.fromstring(text)

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_xml_id} ')]"
        old_tag_element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        old_tag_name = old_tag_element.tag
        old_tag_name = re.sub(r'{.*?}', '', old_tag_name)

        old_tag_attributes = old_tag_element.attrib

        # Add new tag with temp id
        text_result = self.__add_tag(text, start_pos, end_pos, temp_xml_id, annotator_xml_id)

        # Mark old tag to delete
        attributes_to_add = {
            XML_ID_KEY: f'{tag_xml_id}-old',
            'deleted': 'true',
            'saved': 'false',
            'resp': f'#{annotator_xml_id}',
        }

        attributes_to_delete = {
            XML_ID_KEY: tag_xml_id,
        }

        text_result = self.__update_tag_in_body(text_result, tag_xml_id, attributes_to_add=attributes_to_add,
                                                attributes_to_delete=attributes_to_delete)

        # update attributes in new tag
        attributes_to_add = {
            XML_ID_KEY: tag_xml_id,
            'saved': 'false',
            'resp': f'#{annotator_xml_id}',
        }

        attributes_to_add = {**old_tag_attributes, **attributes_to_add}

        attributes_to_delete = {
            XML_ID_KEY: temp_xml_id,
        }

        text_result = self.__update_tag_in_body(text_result, temp_xml_id, new_tag=old_tag_name,
                                                attributes_to_add=attributes_to_add,
                                                attributes_to_delete=attributes_to_delete)

        return text_result

    def add_reference_to_entity(self, text, tag_xml_id, new_tag, new_tag_xml_id, entity_xml_id, annotator_xml_id):
        attributes_to_add = {
            'newId': f'{new_tag_xml_id}',
            'ref': f'#{entity_xml_id}',
            'unsavedRef': f'#{entity_xml_id}',
            'resp': f'#{annotator_xml_id}',
            'saved': 'false',
        }

        text_result = self.__update_tag_in_body(text, tag_xml_id, new_tag=new_tag, attributes_to_add=attributes_to_add)

        return text_result

    def add_attributes_to_tag(self, text, tag_xml_id, attributes_to_add):
        text_result = self.__update_tag_in_body(text, tag_xml_id, attributes_to_add=attributes_to_add)

        return text_result

    def mark_reference_to_delete(self, text, tag_xml_id, entity_xml_id, annotator_xml_id):
        attributes_to_add = {
            'refDeleted': f'#{entity_xml_id}',
            'saved': 'false',
            'resp': f'#{annotator_xml_id}',
        }

        text_result = self.__update_tag_in_body(text, tag_xml_id, attributes_to_add=attributes_to_add)

        return text_result

    @staticmethod
    def check_if_last_reference(text, target_element_id):
        tree = etree.fromstring(text)

        xpath = f"//*[contains(concat(' ', @ref, ' '), ' {target_element_id} ')]"
        all_references = tree.xpath(xpath, namespaces=XML_NAMESPACES)

        if len(all_references) > 1:
            return False
        else:
            return True
