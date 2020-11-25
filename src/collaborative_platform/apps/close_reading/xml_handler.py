import copy
import re

from lxml import etree

from apps.exceptions import BadParameters, Forbidden, UnsavedElement
from apps.close_reading.text_splitter import TextSplitter
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match

from collaborative_platform.settings import XML_NAMESPACES


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class XmlHandler:
    def __init__(self, annotator_xml_id):
        self.__annotator_xml_id = annotator_xml_id

    def add_tag(self, text, start_pos, end_pos, tag_xml_id):
        self.__check_if_positions_are_valid(text, start_pos, end_pos)

        text = self.__add_tag(text, start_pos, end_pos, tag_xml_id)

        attributes = {
            'respAdded': f'#{self.__annotator_xml_id}',
            'saved': 'false',
        }

        text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)

        return text

    def move_tag(self, text, start_pos, end_pos, tag_xml_id):
        temp_xml_id = f'{tag_xml_id}-new'

        # Get tag name
        tree = etree.fromstring(text)

        old_tag_elements = self.get_xml_elements(tree, tag_xml_id)
        old_tag_element = old_tag_elements[0]

        old_tag_name = old_tag_element.tag
        old_tag_name = re.sub(r'{.*?}', '', old_tag_name)

        old_tag_attributes = old_tag_element.attrib

        # Add new tag with temp id
        text = self.__add_tag(text, start_pos, end_pos, temp_xml_id)

        try:
            self.check_if_tag_is_saved(text, tag_xml_id)

        except UnsavedElement:
            # remove old tag
            saved = False

            text = self.__remove_tag(text, tag_xml_id)

        else:
            # Mark old tag to delete
            saved = True

            attributes = {
                XML_ID_KEY: f'{tag_xml_id}-old',
                'deleted': 'true',
            }

            attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

            text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)

        # update attributes in new tag
        attributes = {
            XML_ID_KEY: tag_xml_id,
            'saved': 'false',
        }

        attributes = {**old_tag_attributes, **attributes}

        if 'resp' not in attributes and 'respAdded' not in attributes:
            attributes.update({'respAdded': f'#{self.__annotator_xml_id}'})

        text = self.__update_tag(text, temp_xml_id, new_tag=old_tag_name, attributes_to_set=attributes)

        return text, saved

    def delete_tag(self, text, tag_xml_id):
        self.check_if_tag_is_saved(text, tag_xml_id)

        attributes = {
            'deleted': 'true',
        }

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)

        return text

    def add_reference_to_entity(self, text, tag_xml_id, new_tag, new_tag_xml_id, entity_xml_id):
        attributes = {
            f'{XML_ID_KEY}Added': f'{new_tag_xml_id}',
            f'{XML_ID_KEY}Deleted': f'{tag_xml_id}',
            'refAdded': f'#{entity_xml_id}',
        }

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, new_tag=new_tag, attributes_to_set=attributes)

        return text

    def modify_reference_to_entity(self, text, tag_xml_id, new_entity_xml_id, old_entity_xml_id, new_tag=None,
                                   new_tag_xml_id=None):
        try:
            self.check_if_reference_is_saved(text, tag_xml_id, old_entity_xml_id)

        except UnsavedElement:
            saved = False

            attributes = {
                'refAdded': f'#{new_entity_xml_id}',
            }

        else:
            saved = True

            attributes = {
                'refAdded': f'#{new_entity_xml_id}',
                'refDeleted': f'#{old_entity_xml_id}',
            }

        if new_tag_xml_id:
            attributes.update({
                f'{XML_ID_KEY}Added': f'{new_tag_xml_id}',
                f'{XML_ID_KEY}Deleted': f'{tag_xml_id}',
            })

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, new_tag=new_tag, attributes_to_set=attributes)

        return text, saved

    def delete_reference_to_entity(self, text, tag_xml_id, new_tag, new_tag_xml_id, entity_xml_id):
        self.check_if_reference_is_saved(text, tag_xml_id, entity_xml_id)

        attributes = {
            f'{XML_ID_KEY}Added': f'{new_tag_xml_id}',
            f'{XML_ID_KEY}Deleted': f'{tag_xml_id}',
            'refDeleted': f'#{entity_xml_id}',
        }

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, new_tag=new_tag, attributes_to_set=attributes)

        return text

    def add_entity_properties(self, text, tag_xml_id, entity_properties):
        entity_properties.pop('name', '')

        attributes = {f'{key}Added': value for key, value in entity_properties.items()}

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)

        return text

    def modify_entity_property(self, text, tag_xml_id, old_entity_property, new_entity_property):
        new_entity_property.pop('name', '')
        old_entity_property.pop('name', '')

        try:
            self.__check_if_property_is_saved(text, tag_xml_id, old_entity_property)
        except UnsavedElement:
            attributes = {f'{key}Added': value for key, value in new_entity_property.items()}

            text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)
        else:
            text = self.delete_entity_properties(text, tag_xml_id, old_entity_property)
            text = self.add_entity_properties(text, tag_xml_id, new_entity_property)

        attributes = {}

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)

        return text

    def delete_entity_properties(self, text, tag_xml_id, entity_properties):
        entity_properties.pop('name', '')

        attributes_to_set = {}
        attributes_to_delete = {}

        for property, value in entity_properties.items():
            try:
                self.__check_if_property_is_saved(text, tag_xml_id, {property: value})
            except UnsavedElement:
                attributes_to_delete.update({f'{property}Added': value})
            else:
                attributes_to_set.update({f'{property}Deleted': value})

        attributes_to_set = self.__add_resp_if_needed(attributes_to_set, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes_to_set,
                                 attributes_to_delete=attributes_to_delete)

        return text

    def discard_adding_tag(self, text, tag_xml_id):
        text = self.__remove_tag(text, tag_xml_id)

        return text

    def discard_moving_tag(self, text, tag_xml_id):
        text = self.__remove_tag(text, tag_xml_id)

        old_tag_xml_id = f'{tag_xml_id}-old'

        attributes_to_set = {
            XML_ID_KEY: tag_xml_id
        }

        attributes_to_delete = [
            'deleted',
        ]

        text = self.__update_tag(text, old_tag_xml_id, attributes_to_set=attributes_to_set,
                                 attributes_to_delete=attributes_to_delete)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_deleting_tag(self, text, tag_xml_id):
        attributes_to_delete = [
            'deleted',
        ]

        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes_to_delete)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_adding_reference_to_entity(self, text, tag_xml_id, properties_to_delete=None):
        attributes = [
            'refAdded',
            f'{XML_ID_KEY}Added',
            f'{XML_ID_KEY}Deleted',
        ]

        if properties_to_delete:
            attributes_for_unlistable_entities = {f'{property}Added' for property in properties_to_delete}
            attributes += attributes_for_unlistable_entities

        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_modifying_reference_to_entity(self, text, tag_xml_id, properties_added=None, properties_deleted=None):
        attributes = [
            'refAdded',
            'refDeleted',
            f'{XML_ID_KEY}Added',
            f'{XML_ID_KEY}Deleted',
        ]

        new_tag = tag_xml_id.split('-')[0]

        if properties_added:
            attributes_for_unlistable_entities = {f'{property}Added' for property in properties_added}
            attributes += attributes_for_unlistable_entities

        if properties_deleted:
            attributes_for_unlistable_entities = {f'{property}Deleted' for property in properties_deleted}
            attributes += attributes_for_unlistable_entities

        text = self.__update_tag(text, tag_xml_id, new_tag=new_tag, attributes_to_delete=attributes)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_removing_reference_to_entity(self, text, tag_xml_id, properties_deleted=None):
        attributes = [
            'refDeleted',
            f'{XML_ID_KEY}Added',
            f'{XML_ID_KEY}Deleted',
        ]

        new_tag = tag_xml_id.split('-')[0]

        if properties_deleted:
            attributes_for_unlistable_entities = [f'{property}Deleted' for property in properties_deleted]
            attributes += attributes_for_unlistable_entities

        text = self.__update_tag(text, tag_xml_id, new_tag=new_tag, attributes_to_delete=attributes)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_adding_entity_property(self, text, tag_xml_id, property_added):
        attributes = [
            f'{property_added}Added'
        ]

        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_modifying_entity_property(self, text, tag_xml_id, property_modified):
        attributes = [
            f'{property_modified}Added',
            f'{property_modified}Deleted',
        ]

        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def discard_removing_entity_property(self, text, tag_xml_id, property_deleted):
        attributes = [
            f'{property_deleted}Deleted',
        ]

        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes)
        text = self.__remove_resp_if_needed(text, tag_xml_id)

        return text

    def accept_adding_tag(self, text, tag_xml_id):
        attributes_to_delete = ['saved']
        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes_to_delete)

        attributes_to_save = ['resp']
        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        return text

    def accept_moving_tag(self, text, tag_xml_id):
        attributes_to_delete = ['saved']
        text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes_to_delete)

        attributes_to_save = ['resp']
        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        text = self.__remove_tag(text, f'{tag_xml_id}-old')

        return text

    def accept_deleting_tag(self, text, tag_xml_id):
        text = self.__remove_tag(text, tag_xml_id)

        return text

    def accept_adding_reference_to_entity(self, text, tag_xml_id, properties_added=None):
        attributes_to_save = [
            'ref',
            XML_ID_KEY,
        ]

        if properties_added:
            attributes_to_save += properties_added

        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        return text

    def accept_modifying_reference_to_entity(self, text, tag_xml_id, properties_added=None,
                                             properties_deleted=None):
        if properties_deleted:
            properties_deleted = [key for key, value in properties_deleted.items()]

            text = self.__delete_attributes_in_tag(text, tag_xml_id, properties_deleted)

        attributes_to_save = [
            'ref',
            'resp',
            XML_ID_KEY,
        ]

        if properties_added:
            properties_added = [key for key, value in properties_added.items()]

            attributes_to_save += properties_added

        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        return text

    def accept_removing_reference_to_entity(self, text, tag_xml_id, properties_deleted=None):
        attributes_to_delete = [
            'ref'
        ]

        if properties_deleted:
            properties_deleted = [key for key, value in properties_deleted.items()]

            attributes_to_delete += properties_deleted

        text = self.__delete_attributes_in_tag(text, tag_xml_id, attributes_to_delete)

        attributes_to_save = [
            'resp',
            XML_ID_KEY,
        ]

        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        return text

    def accept_adding_entity_property(self, text, tag_xml_id, property_added):
        attributes_to_save = [
            'resp'
        ]

        if property_added:
            attributes_to_save.append(property_added)

        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        return text

    def accept_modifying_entity_property(self, text, tag_xml_id, property_modified):
        attributes_to_save = [
            'resp'
        ]

        if property_modified:
            attributes_to_save.append(property_modified)

        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        return text

    def accept_removing_entity_property(self, text, tag_xml_id, property_deleted):
        attributes_to_save = [
            'resp'
        ]

        text = self.__save_attributes_in_tag(text, tag_xml_id, attributes_to_save)

        attributes_to_delete = [property_deleted]

        text = self.__delete_attributes_in_tag(text, tag_xml_id, attributes_to_delete)

        return text

    def check_permissions(self, text,  tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_elements(tree, tag_xml_id)[0]

        resp = element.attrib.get('resp')
        resp_added = element.attrib.get('respAdded')

        if resp_added:
            if resp_added != f'#{self.__annotator_xml_id}':
                raise Forbidden
        elif resp:
            if resp != f'#{self.__annotator_xml_id}':
                raise Forbidden

    @staticmethod
    def check_if_last_reference(text, target_element_id):
        tree = etree.fromstring(text)

        xpath = f"//*[contains(concat(' ', @ref, ' '), ' {target_element_id} ')]"
        references = tree.xpath(xpath, namespaces=XML_NAMESPACES)

        xpath = f"//*[contains(concat(' ', @refAdded, ' '), ' {target_element_id} ')]"
        added_references = tree.xpath(xpath, namespaces=XML_NAMESPACES)

        all_references = set(references) | set(added_references)

        if len(all_references) > 1:
            return False
        else:
            return True

    @staticmethod
    def __check_if_positions_are_valid(text, start_pos, end_pos):
        if start_pos >= end_pos:
            raise BadParameters(f"'start_pos' or 'end_pos' parameter is not valid. 'start_pos' parameter must be less "
                                f"than 'end_pos' parameter. 'start_pos': {start_pos}, 'end_pos': {end_pos}")

        selected_fragment = text[start_pos:end_pos]

        regex = r'^[^<]*?>'
        match = re.search(regex, selected_fragment)

        if match:
            raise BadParameters(f"'start_pos' parameter is not valid. Selected fragment can't start or end "
                                f"in the middle of the tag. Selected fragment: '{selected_fragment}'")

        regex = r'<[^>]*?$'
        match = re.search(regex, selected_fragment)

        if match:
            raise BadParameters(f"'end_pos' parameter is not valid. Selected fragment can't start or end "
                                f"in the middle of the tag. Selected fragment: '{selected_fragment}'")

    def __add_resp_if_needed(self, attributes, text, tag_xml_id):
        resp_in_tag = self.__check_if_resp_in_tag(text, tag_xml_id)

        if not resp_in_tag:
            attributes.update({'respAdded': f'#{self.__annotator_xml_id}'})

        return attributes

    def __remove_resp_if_needed(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        attributes = str(element.attrib)

        regex = r'(?<!resp)Added'
        matches = re.findall(regex, attributes)

        saved = element.attrib.get('saved')

        if len(matches) == 0 and saved is None:
            attributes = ['respAdded']

            text = self.__update_tag(text, tag_xml_id, attributes_to_delete=attributes)

        return text

    def __save_attributes_in_tag(self, text, tag_xml_id, attributes_to_save):
        tree = etree.fromstring(text)
        elements = self.get_xml_elements(tree, tag_xml_id)

        for element in elements:
            for attribute in attributes_to_save:
                try:
                    attribute_value = element.attrib.pop(f'{attribute}Added')
                    element.set(attribute, attribute_value)

                except KeyError:
                    pass

                try:
                    element.attrib.pop(f'{attribute}Deleted')

                except KeyError:
                    pass

        text = etree.tounicode(tree, pretty_print=True)

        return text

    def __delete_attributes_in_tag(self, text, tag_xml_id, attributes_to_delete):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        for attribute in attributes_to_delete:
            try:
                element.attrib.pop(f'{attribute}Deleted')
                element.attrib.pop(attribute)

            except KeyError:
                pass

        text = etree.tounicode(tree, pretty_print=True)

        return text

    def check_if_tag_is_saved(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_elements(tree, tag_xml_id)[0]
        saved = element.attrib.get('saved')

        if saved == 'false':
            raise UnsavedElement

    def check_if_reference_is_saved(self, text, tag_xml_id, entity_xml_id=None):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)
        reference = element.attrib.get('ref')

        if entity_xml_id:
            if reference != f'#{entity_xml_id}':
                raise UnsavedElement

        else:
            if not reference:
                raise UnsavedElement

    def __check_if_property_is_saved(self, text, tag_xml_id, entity_property):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        property_name = list(entity_property.items())[0][0]
        property_value = list(entity_property.items())[0][1]

        property_value_in_file = element.attrib.get(f'{property_name}Added')

        if property_value_in_file == property_value:
            raise UnsavedElement

    def check_if_tag_is_an_entity(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        xml_id = element.attrib.get(XML_ID_KEY)
        ref = element.attrib.get('ref')
        ref = ref.replace('#', '') if ref else ref

        xml_id_added = element.attrib.get(f'{XML_ID_KEY}Added')
        ref_added = element.attrib.get('refAdded')
        ref_added = ref_added.replace('#', '') if ref_added else ref_added

        if xml_id == ref:
            return True

        elif xml_id_added is not None and xml_id_added == ref_added:
            return True

        else:
            return False

    def __check_if_resp_in_tag(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_elements(tree, tag_xml_id)[0]

        resp = element.attrib.get('resp')
        resp_added = element.attrib.get('respAdded')

        if resp is not None or resp_added is not None:
            return True
        else:
            return False

    @staticmethod
    def __add_tag(text, start_pos, end_pos, tag_xml_id):
        text_before = text[:start_pos]
        text_inside = text[start_pos:end_pos]
        text_after = text[end_pos:]

        text_in_parts = TextSplitter().split_text_to_autonomic_parts(text_inside)
        parts_to_tag_nr = TextSplitter().count_parts_to_tag(text_in_parts)

        tagged_parts = []
        index = 0

        for part in text_in_parts:
            tag_regex = r'<.*?>'
            whitespace_regex = r'\s'

            cleaned_tags = re.sub(tag_regex, '', part)
            cleaned_whitespaces = re.sub(whitespace_regex, '', cleaned_tags)

            if cleaned_whitespaces:
                new_tag_xml_id = tag_xml_id

                if parts_to_tag_nr > 1:
                    if new_tag_xml_id.endswith('-new'):
                        new_tag_xml_id = new_tag_xml_id.replace('-new', '')
                        new_tag_xml_id = f'{new_tag_xml_id}.{index}-new'
                    else:
                        new_tag_xml_id = f'{new_tag_xml_id}.{index}'

                tagged_part = f'<seg xml:id="{new_tag_xml_id}">{part}</seg>'

                tagged_parts.append(tagged_part)
                index += 1

            else:
                tagged_parts.append(part)

        joined_parts = ''.join(tagged_parts)

        text = text_before + joined_parts + text_after

        return text

    def __remove_tag(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        elements = self.get_xml_elements(tree, tag_xml_id)

        for element in elements:
            parent = element.getparent()

            if element.text:
                previous_sibling = element.getprevious()

                if previous_sibling is not None:
                    if previous_sibling.tail:
                        previous_sibling.tail += element.text
                    else:
                        previous_sibling.tail = element.text

                else:
                    if parent.text:
                        parent.text += element.text
                    else:
                        parent.text = element.text

            for child in element.iterchildren():
                element.addprevious(child)

            if element.tail:
                previous_sibling = element.getprevious()

                if previous_sibling is not None:
                    previous_sibling.tail = str(previous_sibling.tail) + element.tail
                else:
                    parent.text = str(parent.text) + element.tail

            parent.remove(element)

        text = etree.tounicode(tree, pretty_print=True)

        return text

    def __update_tag(self, text, tag_xml_id, new_tag=None, attributes_to_set=None, attributes_to_delete=None):
        tree = etree.fromstring(text)
        elements = self.get_xml_elements(tree, tag_xml_id)

        for element in elements:
            if attributes_to_set:
                updated_attributes = copy.deepcopy(attributes_to_set)
                attributes_with_xml_id = [XML_ID_KEY, f'{XML_ID_KEY}Added', f'{XML_ID_KEY}Deleted']

                for attribute_name in attributes_with_xml_id:
                    if attribute_name in updated_attributes:
                        attribute_value = updated_attributes[attribute_name]
                        updated_attribute_value = self.__update_xml_id_attribute(element, attribute_value)

                        updated_attributes[attribute_name] = updated_attribute_value

                for attribute, value in sorted(updated_attributes.items()):
                    element.set(attribute, value)

            if attributes_to_delete:
                for attribute in attributes_to_delete:
                    element.attrib.pop(attribute, '')

            references = element.attrib.get('ref')

            if references:
                references = set(references.split(' '))
            else:
                references = set()

            references_added = element.attrib.get('refAdded')

            if references_added:
                references_added = set(references_added.split(' '))
            else:
                references_added = set()

            references_deleted = element.attrib.get('refDeleted')

            if references_deleted:
                references_deleted = set(references_deleted.split(' '))
            else:
                references_deleted = set()

            remaining_references = (references | references_added) - references_deleted
            if not remaining_references:
                prefix = "{%s}" % XML_NAMESPACES['default']
                tag = prefix + 'seg'
                element.tag = tag

            if new_tag:
                prefix = "{%s}" % XML_NAMESPACES['default']
                tag = prefix + new_tag
                element.tag = tag

        text = etree.tounicode(tree, pretty_print=True)

        return text

    @staticmethod
    def __update_xml_id_attribute(element, xml_id_value):
        new_xml_id_split = xml_id_value.split('-')
        new_xml_id_core = '-'.join(new_xml_id_split[:2])

        if len(new_xml_id_split) == 2:
            new_xml_id_suffix = ''
        else:
            new_xml_id_suffix = new_xml_id_split[2]

        old_xml_id = element.attrib.get(XML_ID_KEY)

        old_xml_id_split = old_xml_id.split('-')

        if '.' in old_xml_id_split[1]:
            old_xml_id_index = old_xml_id_split[1].split('.')[1]
        else:
            old_xml_id_index = ''

        updated_xml_id = new_xml_id_core

        if old_xml_id_index:
            updated_xml_id = f'{updated_xml_id}.{old_xml_id_index}'

        if new_xml_id_suffix:
            updated_xml_id = f'{updated_xml_id}-{new_xml_id_suffix}'

        return updated_xml_id

    @staticmethod
    def get_xml_element(tree, tag_xml_id):
        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_xml_id}.')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if element is None:
            xpath = f"//*[contains(concat(' ', @xml:idAdded, ' '), ' {tag_xml_id}.')]"
            element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if element is None:
            xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_xml_id} ')]"
            element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if element is None:
            xpath = f"//*[contains(concat(' ', @xml:idAdded, ' '), ' {tag_xml_id} ')]"
            element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        return element

    @staticmethod
    def get_xml_elements(tree, tag_xml_id):
        # TODO: Try to update xpath to get proper xml elements without additional filtering in Python

        if tag_xml_id.endswith('-old') or tag_xml_id.endswith('-new'):
            split_tag = tag_xml_id.split('-')
            tag_core = '-'.join(split_tag[:-1])
            suffix = split_tag[-1]
        else:
            tag_core = tag_xml_id
            suffix = ''

        xpaths = [
            f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_core}.')]",
            f"//*[contains(concat(' ', @xml:idAdded, ' '), ' {tag_core}.')]",
            f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_core}-')]",
            f"//*[contains(concat(' ', @xml:idAdded, ' '), ' {tag_core}-')]",
            f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_core} ')]",
            f"//*[contains(concat(' ', @xml:idAdded, ' '), ' {tag_core} ')]",
        ]

        all_elements = []

        for xpath in xpaths:
            elements = tree.xpath(xpath, namespaces=XML_NAMESPACES)
            all_elements += elements

        elements = set(all_elements)

        if suffix:
            elements = [element for element in elements if element.attrib[XML_ID_KEY].endswith(f'-{suffix}')]
        else:
            elements = [element for element in elements if not
                        (element.attrib[XML_ID_KEY].endswith('-old') or element.attrib[XML_ID_KEY].endswith('-new'))]

        return elements

    def get_connected_xml_ids(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        tag_xml_ids = tag_xml_id.split('/')[0]

        elements = self.get_xml_elements(tree, tag_xml_ids)

        xml_ids = []

        for element in elements:
            xml_id = element.attrib.get(XML_ID_KEY)
            xml_ids.append(xml_id)

        return xml_ids

    @staticmethod
    def switch_body_content(old_xml_content, new_body_content):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(old_xml_content, parser=parser)

        body_xpath = './default:text'
        old_body_element = get_first_xpath_match(tree, body_xpath, XML_NAMESPACES)

        body_parent = old_body_element.getparent()
        body_parent.remove(old_body_element)

        new_body_element = etree.fromstring(new_body_content, parser=parser)
        body_parent.append(new_body_element)

        new_xml_content = etree.tounicode(tree, pretty_print=True)

        return new_xml_content
