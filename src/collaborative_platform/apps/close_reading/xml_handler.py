import re

from lxml import etree

from apps.exceptions import UnsavedElement
from apps.files_management.file_conversions.xml_tools import get_first_xpath_match

from collaborative_platform.settings import XML_NAMESPACES


XML_ID_KEY = f"{{{XML_NAMESPACES['xml']}}}id"


class XmlHandler:
    def __init__(self, annotator_xml_id):
        self.__annotator_xml_id = annotator_xml_id

    def add_tag(self, text, start_pos, end_pos, tag_xml_id):
        text_before = text[:start_pos]
        text_inside = text[start_pos:end_pos]
        text_after = text[end_pos:]

        text = f'{text_before}<ab xml:id="{tag_xml_id}">{text_inside}</ab>{text_after}'

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

        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_xml_id} ')]"
        old_tag_element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        old_tag_name = old_tag_element.tag
        old_tag_name = re.sub(r'{.*?}', '', old_tag_name)

        old_tag_attributes = old_tag_element.attrib

        # Add new tag with temp id
        text = self.add_tag(text, start_pos, end_pos, temp_xml_id)

        try:
            self.__check_if_tag_is_saved(text, tag_xml_id)

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
        }

        attributes = {**old_tag_attributes, **attributes}

        text = self.__update_tag(text, temp_xml_id, new_tag=old_tag_name, attributes_to_set=attributes)

        return text, saved

    def delete_tag(self, text, tag_xml_id):
        self.__check_if_tag_is_saved(text, tag_xml_id)

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

        return text

    def delete_reference_to_entity(self, text, tag_xml_id, new_tag, new_tag_xml_id, entity_xml_id):
        self.__check_if_reference_is_saved(text, tag_xml_id, entity_xml_id)

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

        attributes = {f'{key}Deleted': value for key, value in entity_properties.items()}

        attributes = self.__add_resp_if_needed(attributes, text, tag_xml_id)

        text = self.__update_tag(text, tag_xml_id, attributes_to_set=attributes)

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
        element = self.get_xml_element(tree, tag_xml_id)

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

    def __check_if_tag_is_saved(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)
        saved = element.attrib.get('saved')

        if saved == 'false':
            raise UnsavedElement

    def __check_if_reference_is_saved(self, text, tag_xml_id, entity_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)
        reference_added = element.attrib.get('refAdded')

        if reference_added == f'#{entity_xml_id}':
            raise UnsavedElement

    def __check_if_property_is_saved(self, text, tag_xml_id, entity_property):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        property_name = list(entity_property.items())[0][0]
        property_value = list(entity_property.items())[0][1]

        property_value_in_file = element.attrib.get(f'{property_name}Added')

        if property_value_in_file == property_value:
            raise UnsavedElement

    def __check_if_resp_in_tag(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        resp = element.attrib.get('resp')
        resp_added = element.attrib.get('respAdded')

        if resp is not None or resp_added is not None:
            return True
        else:
            return False

    def __remove_tag(self, text, tag_xml_id):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        parent = element.getparent()

        if element.text != '':
            previous_sibling = element.getprevious()

            if previous_sibling is not None:
                previous_sibling.tail += element.text
            else:
                parent.text += element.text

        for child in element.iterchildren():
            element.addprevious(child)

        if element.tail != '':
            previous_sibling = element.getprevious()

            if previous_sibling is not None:
                previous_sibling.tail += element.tail
            else:
                parent.text += element.tail

        parent.remove(element)

        text = etree.tounicode(tree, pretty_print=True)

        return text

    def __update_tag(self, text, tag_xml_id, new_tag=None, attributes_to_set=None, attributes_to_delete=None):
        tree = etree.fromstring(text)
        element = self.get_xml_element(tree, tag_xml_id)

        if attributes_to_set:
            for attribute, value in sorted(attributes_to_set.items()):
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
            tag = prefix + 'ab'
            element.tag = tag

        if new_tag:
            prefix = "{%s}" % XML_NAMESPACES['default']
            tag = prefix + new_tag
            element.tag = tag

        text = etree.tounicode(tree, pretty_print=True)

        return text

    @staticmethod
    def get_xml_element(tree, tag_xml_id):
        xpath = f"//*[contains(concat(' ', @xml:id, ' '), ' {tag_xml_id} ')]"
        element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        if element is None:
            xpath = f"//*[contains(concat(' ', @xml:idAdded, ' '), ' {tag_xml_id} ')]"
            element = get_first_xpath_match(tree, xpath, XML_NAMESPACES)

        return element

    @staticmethod
    def switch_body_content(old_xml_content, new_body_content):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(old_xml_content, parser=parser)

        body_xpath = './default:text/default:body'
        old_body_element = get_first_xpath_match(tree, body_xpath, XML_NAMESPACES)

        body_parent = old_body_element.getparent()
        body_parent.remove(old_body_element)

        new_body_element = etree.fromstring(new_body_content, parser=parser)
        body_parent.append(new_body_element)

        new_xml_content = etree.tounicode(tree, pretty_print=True)

        return new_xml_content
