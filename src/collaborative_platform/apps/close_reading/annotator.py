import re
from lxml import etree
from django.contrib.auth.models import User

from apps.files_management.models import FileMaxXmlIds, File

import logging
logger = logging.getLogger(__name__)

NAMESPACES = {
    'default': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xi': 'http://www.w3.org/2001/XInclude',
}


class NotModifiedException(Exception):
    pass


class Annotator:
    def __init__(self):
        self.__xml = ""
        self.__file = None
        self.__json = {}
        self.__annotator_xml_id = ""

        self.__start = 0
        self.__end = 0
        self.__fragment_to_annotate = ""
        self.__tags = {}
        self.__annotators_xml_ids = []
        self.__tag_xml_id_number = 0
        self.__certainty_xml_id_number = 0

        self.__fragment_annotated = ""
        self.__certainty_to_add = None
        self.__annotator_to_add = None

        self.__xml_annotated = ""

    def add_annotation(self, xml, file_id, json, annotator_guid):
        self.__xml = xml
        self.__file = File.objects.get(id=file_id)
        self.__annotator_xml_id = 'person' + str(annotator_guid)

        self.__json = self.__validate_request(json)

        self.__get_data_from_xml()
        self.__prepare_xml_parts()
        self.__check_if_new_elements_already_exist()
        self.__create_new_xml()

        return self.__xml_annotated

    def __validate_request(self, json):
        position_params_v1 = [
            'start_row',
            'start_col',
            'end_row',
            'end_col',
        ]

        position_params_v2 = [
            'start_pos',
            'end_pos',
        ]

        optional_params = [
            'category',
            'locus',
            'certainty',
            'asserted_value',
            'description',
            'tag',
            'attribute_name',
        ]

        position_v1 = all(elements in json.keys() for elements in position_params_v1)
        position_v2 = all(elements in json.keys() for elements in position_params_v2)

        if not (position_v1 or position_v2):
            raise ValueError("No position arguments in request.")

        positions_to_check = position_params_v1 if position_v1 else position_params_v2

        for position in positions_to_check:
            if not isinstance(json[position], int):
                raise TypeError("Value of '{}' is not a integer.".format(position))

            if json[position] <= 0:
                raise ValueError("Value of '{}' must be a positive number.".format(position))

        validated_json = {}

        if position_v1:
            start, end = self.__get_fragment_position(self.__xml, json)

            validated_json.update({'start_pos': start, 'end_pos': end})
        else:
            validated_json.update({'start_pos': json['start_pos'], 'end_pos': json['end_pos']})

        if validated_json['start_pos'] >= validated_json['end_pos']:
            raise ValueError("Start position of annotating fragment is greater or equal to end position.")

        for param in optional_params:
            if param in json and json[param] is not None:
                validated_json.update({param: json[param]})
            else:
                validated_json.update({param: ''})

        return validated_json

    def __get_data_from_xml(self):
        self.__start, self.__end = self.__get_fragment_position(self.__xml, self.__json)
        self.__start, self.__end = self.__get_fragment_position_without_adhering_tags(self.__xml, self.__start, self.__end)

        self.__start, self.__end = self.__get_fragment_position_with_adhering_tags(self.__xml, self.__start, self.__end)
        self.__fragment_to_annotate = self.__xml[self.__start: self.__end]

        self.__tags = self.__get_adhering_tags_from_annotated_fragment(self.__fragment_to_annotate)
        self.__annotators_xml_ids = self.__get_annotators_xml_ids_from_file(self.__xml)
        certainties = self.__get_certainties_from_file(self.__xml)
        self.__tag_xml_id_number = self.__get_xml_id_number_for_tag(certainties, self.__json["tag"])
        self.__certainty_xml_id_number = self.__get_xml_id_number_for_tag(certainties, 'certainty')

    def __get_fragment_position(self, xml, json):
        if 'start_pos' in json and json['start_pos'] is not None and 'end_pos' in json and json['end_pos'] is not None:
            start = json['start_pos']
            end = json['end_pos']

        else:
            start, end = self.__convert_rows_and_cols_to_start_and_end(xml, json["start_row"], json["start_col"],
                                                                       json["end_row"], json["end_col"])

        return start, end

    @staticmethod
    def __convert_rows_and_cols_to_start_and_end(text, start_row, start_col, end_row, end_col):
        text_in_lines = text.splitlines(True)

        chars_to_start = 0
        chars_to_end = 0

        i = 0
        while i + 1 < start_row:
            chars_to_start += len(text_in_lines[i])
            i += 1

        chars_to_start += start_col - 1

        j = 0
        while j + 1 < end_row:
            chars_to_end += len(text_in_lines[j])
            j += 1

        chars_to_end += end_col

        return chars_to_start, chars_to_end

    @staticmethod
    def __get_fragment_position_without_adhering_tags(string, start, end):
        found_tag = True

        while found_tag:
            found_tag = False

            marked_fragment = string[start:end]

            match = re.search(r'^\s*<[^<>]*?>\s*', marked_fragment)
            if match is not None:
                tag_open = match.group()
                start += len(tag_open)
                found_tag = True

            match = re.search(r'\s*<[^<>]*?>\s*$', marked_fragment)
            if match is not None:
                tag_close = match.group()
                end -= len(tag_close)
                found_tag = True

        return start, end

    @staticmethod
    def __get_fragment_position_with_adhering_tags(string, start, end):
        found_tag = True

        while found_tag:
            found_tag = False

            text_before = string[:start]
            text_after = string[end:]

            match = re.search(r'<[^<>]*?>\s*?$', text_before)
            if match is not None:
                tag_open = match.group()
                start -= len(tag_open)
                found_tag = True

            match = re.search(r'^\s*?<[^<>]*?>', text_after)
            if match is not None:
                tag_close = match.group()
                end += len(tag_close)
                found_tag = True

        return start, end

    @staticmethod
    def __get_adhering_tags_from_annotated_fragment(fragment):
        tags = {}

        while re.search(r'^\s*?<[^<>]*?>', fragment):
            match = re.search(r'^\s*?<[^<>]*?>', fragment)

            tag_raw = match.group()
            tag = tag_raw.strip()
            tag_name = tag

            marks_to_remove = ['</', '<', '/>', '>']

            for mark in marks_to_remove:
                tag_name = tag_name.replace(mark, '')

            tag_name = tag_name.split(' ')[0]

            tag_to_add = {tag_name: {}}

            arguments = re.findall(r'[\w:]+=".*?"', tag)

            for argument in arguments:
                arg_name = re.search(r'[\w:]+="', argument)
                arg_name = arg_name.group()
                arg_name = arg_name.replace('="', '')

                arg_value = re.search(r'".*?"', argument)
                arg_value = arg_value.group()
                arg_value = arg_value.replace('"', '')

                tag_to_add[tag_name].update({arg_name: arg_value})

            tags.update(tag_to_add)
            fragment = fragment[len(tag_raw):]

        return tags

    @staticmethod
    def __get_certainties_from_file(text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        certainties = tree.xpath('//default:teiHeader'
                                 '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]'
                                 '/default:certainty', namespaces=NAMESPACES)

        return certainties

    @staticmethod
    def __get_annotators_xml_ids_from_file(text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = text

        tree = etree.fromstring(text_to_parse)

        annotators = tree.xpath('//default:teiHeader'
                                '//default:listPerson[@type="PROVIDEDH Annotators"]'
                                '/default:person', namespaces=NAMESPACES)

        xml_ids = []
        for annotator in annotators:
            prefix = '{%s}' % NAMESPACES['xml']
            xml_id = annotator.get(prefix + 'id')

            xml_ids.append(xml_id)

        return xml_ids

    def __get_xml_id_number_for_tag(self, certainties, tag='ab'):
        if tag in ['event', 'org', 'person', 'place', 'certainty']:
            file_mx_xml_id = FileMaxXmlIds.objects.get(file=self.__file)

            file_mx_xml_id.__dict__[tag] += 1
            file_mx_xml_id.save()

            return file_mx_xml_id.__dict__[tag]

        # TODO: Max IDs for all tags in file should be keep in database
        else:
            biggest_number = 0

            for certainty in certainties:
                id_value = certainty.attrib['target']

                if tag not in id_value:
                    continue

                id_value = id_value.strip()

                split_values = id_value.split(' ')
                for value in split_values:
                    number = value.replace('#' + tag, '')
                    number = int(number)

                    if number > biggest_number:
                        biggest_number = number

            return biggest_number + 1

    def __prepare_xml_parts(self):
        # 1.Add tag to text
        if self.__json['locus'] == '' and self.__json['tag'] != '' and self.__json['attribute_name'] == '':
            self.__fragment_annotated, _ = self.__add_tag(self.__fragment_to_annotate, self.__json["tag"])

        # 2.Add certainty without tag to text
        elif self.__json['locus'] == 'value' and self.__json['tag'] == '' and self.__json['attribute_name'] == '':
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, 'ab',
                                                                       uncertainty=True)
            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 3.Add certainty with tag to text
        elif self.__json['locus'] == 'value' and self.__json['tag'] != '' and self.__json['attribute_name'] == '':
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, self.__json["tag"],
                                                                       uncertainty=True)
            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 4.Add certainty to tag
        elif self.__json['locus'] == 'name' and self.__json['tag'] != '' and self.__json['attribute_name'] == '':
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, self.__json["tag"],
                                                                       uncertainty=True)
            self.__certainty_to_add = self.__create_certainty_description(self.__json, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

            if self.__json['tag'] not in self.__tags and self.__json['asserted_value'] != '':
                raise ValueError("You can't add asserted value for tag name when you creating new tag.")

        # 5.Add reference to tag
        elif self.__json['locus'] == 'value' and self.__json['tag'] != '' and \
                self.__json['attribute_name'] == 'sameAs' and self.__json['asserted_value'] != '':
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, self.__json["tag"],
                                                                       uncertainty=True)
            self.__certainty_to_add = self.__create_certainty_description_for_attribute(self.__json, annotation_ids,
                                                                                        self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 6.Add attribute to tag
        elif self.__json['locus'] == 'value' and self.__json['tag'] != '' and \
                self.__json['attribute_name'] != '' and self.__json['asserted_value'] != '':
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, self.__json["tag"],
                                                                       uncertainty=True)
            self.__certainty_to_add = self.__create_certainty_description_for_attribute(self.__json, annotation_ids,
                                                                                        self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        else:
            raise ValueError("There is no method to modify xml according to given parameters.")

    def __add_tag(self, annotated_fragment, tag, uncertainty=False):
        new_annotated_fragment = ''
        annotation_ids = []

        while len(annotated_fragment) > 0:
            # handle xml tag
            if re.search(r'^\s*?<[^<>]*?>', annotated_fragment):
                match = re.search(r'^\s*?<[^<>]*?>', annotated_fragment)
                tag_to_move = match.group()

                end_tag = '</' + tag
                empty_tag = '<' + tag + '/'

                if tag in tag_to_move and end_tag not in tag_to_move and empty_tag not in tag_to_move:
                    match = re.search(r'<[^>\s]+', tag_to_move)
                    tag_begin = match.group()

                    if 'xml:id="' not in tag_to_move:
                        id = f"{tag}_{self.__file.name}-{self.__tag_xml_id_number}"
                        attribute = ' xml:id="{0}"'.format(id)

                        annotation_ids.append('#' + id)

                        new_tag_to_move = "{0}{1}{2}".format(tag_to_move[:len(tag_begin)], attribute,
                                                             tag_to_move[len(tag_begin):])

                        self.__tag_xml_id_number += 1
                    else:
                        match = re.search(r'xml:id=".*?"', tag_to_move)
                        existing_id = match.group()
                        existing_id = existing_id.replace('xml:id="', '')
                        existing_id = existing_id.replace('"', '')

                        annotation_ids.append('#' + existing_id)
                        new_tag_to_move = tag_to_move

                    new_annotated_fragment += new_tag_to_move
                else:
                    new_annotated_fragment += tag_to_move

                annotated_fragment = annotated_fragment[len(tag_to_move):]

            # handle text
            else:
                match = re.search(r'^\s*[^<>]+', annotated_fragment)
                text_to_move = match.group()

                if tag in self.__tags:
                    new_annotated_fragment += text_to_move

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                else:
                    attribute = ""

                    if uncertainty:
                        id = f"{tag}_{self.__file.name}-{self.__tag_xml_id_number}"
                        attribute = ' xml:id="{0}"'.format(id)

                        annotation_ids.append('#' + id)

                    tag_open = '<{0}{1}>'.format(tag, attribute)
                    tag_close = '</{0}>'.format(tag)

                    new_annotated_fragment += tag_open + text_to_move + tag_close

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                    if uncertainty:
                        self.__tag_xml_id_number += 1

        return new_annotated_fragment, annotation_ids

    def __create_certainty_description(self, json, annotation_ids, user_uuid):
        target = " ".join(annotation_ids)
        xml_id = f"certainty_{self.__file.name}-{self.__certainty_xml_id_number}"

        certainty = f'<certainty category="{json["category"]}" locus="{json["locus"]}" cert="{json["certainty"]}" ' \
                    f'resp="#{user_uuid}" target="{target}" xml:id="{xml_id}"/>'

        new_element = etree.fromstring(certainty)

        if json["asserted_value"]:
            new_element.set('assertedValue', json["asserted_value"])

        if json["description"]:
            description = etree.Element("desc")
            description.text = json["description"]

            new_element.append(description)

        return new_element

    def __create_certainty_description_for_attribute(self, json, annotation_ids, user_uuid):
        target = " ".join(annotation_ids)
        xml_id = f"certainty_{self.__file.name}-{self.__certainty_xml_id_number}"

        certainty = f'<certainty category="{json["category"]}" locus="{json["locus"]}" cert="{json["certainty"]}" ' \
                    f'resp="#{user_uuid}" target="{target}" match="@{json["attribute_name"]}"' \
                    f'assertedValue="{json["asserted_value"]}" xml:id="{xml_id}"/>'

        new_element = etree.fromstring(certainty)

        if json["description"]:
            description = etree.Element("desc")
            description.text = json["description"]

            new_element.append(description)

        return new_element

    def __create_annotator(self, user_xml_id):
        user_guid = user_xml_id.replace('person', '')

        annotator_data = self.__get_user_data_from_db(user_guid)

        annotator = u"""
            <person xml:id="{0}">
              <persName>
                <forename>{1}</forename>
                <surname>{2}</surname>
                <email>{3}</email>
              </persName>
              <link>{4}</link>
            </person>
        """.format(user_xml_id, annotator_data['forename'], annotator_data['surname'], annotator_data['email'],
                   annotator_data['link'])

        annotator_xml = etree.fromstring(annotator)

        return annotator_xml

    @staticmethod
    def __get_user_data_from_db(user_id):
        user = User.objects.get(id=user_id)

        data = {
            'forename': user.first_name,
            'surname': user.last_name,
            'email': user.email,
            'link': 'https://providedh.ehum.psnc.pl/user/' + user_id + '/',
        }

        return data

    def __check_if_new_elements_already_exist(self):
        if self.__json['locus'] == '' and self.__json['tag'] in self.__tags:
            raise NotModifiedException('This tag already exist.')

        if self.__certainty_to_add is not None:
            xml = self.__xml

            xml_in_lines = xml.splitlines()
            if 'encoding=' in xml_in_lines[0]:
                xml = '\n'.join(xml_in_lines[1:])

            tree = etree.fromstring(xml)
            xpath = '//default:teiHeader' \
                    '//default:classCode[' \
                    '@scheme="http://providedh.eu/uncertainty/ns/1.0"]' \
                    '//default:certainty[' \
                    '@category="{0}" and ' \
                    '@locus="{1}" and ' \
                    '@cert="{2}" and ' \
                    '@target="{3}"'.format(self.__certainty_to_add.attrib['category'],
                                           self.__certainty_to_add.attrib['locus'],
                                           self.__certainty_to_add.attrib['cert'],
                                           self.__certainty_to_add.attrib['target'])

            if self.__json['asserted_value']:
                xpath += ' and @assertedValue="{0}"'.format(self.__json['asserted_value'])

            xpath += ']'

            existing_certainties = tree.xpath(xpath, namespaces=NAMESPACES)

            if existing_certainties and self.__json['description']:
                descriptions = tree.xpath(xpath + '/default:desc', namespaces=NAMESPACES)

                for desc in descriptions:
                    if desc.text == self.__json['description']:
                        raise NotModifiedException('This certainty already exist.')

            elif existing_certainties and not self.__json['description']:
                raise NotModifiedException('This certainty already exist.')

    def __create_new_xml(self):
        xml_annotated = self.__add_tagged_string(self.__xml, self.__fragment_annotated)

        xml_annotated_in_lines = xml_annotated.splitlines()
        if 'encoding=' in xml_annotated_in_lines[0]:
            xml_annotated = '\n'.join(xml_annotated_in_lines[1:])

        if self.__annotator_xml_id not in self.__annotators_xml_ids and self.__annotator_to_add is not None:
            xml_annotated = self.__add_annotator(xml_annotated, self.__annotator_to_add)

        if self.__certainty_to_add is not None:
            xml_annotated = self.__add_certainty(xml_annotated, self.__certainty_to_add)

        xml_annotated = self.__reformat_xml(xml_annotated)

        if 'encoding=' in xml_annotated_in_lines[0]:
            xml_annotated = '\n'.join((xml_annotated_in_lines[0], xml_annotated))

        if 'xml version="' not in xml_annotated:
            xml_annotated = '\n'.join((u'<?xml version="1.0"?>', xml_annotated))

        self.__xml_annotated = xml_annotated

    def __add_tagged_string(self, xml, new_fragment):
        new_xml = xml[:self.__start] + new_fragment + xml[self.__end:]

        return new_xml

    def __add_annotator(self, text, annotator):
        tree = etree.fromstring(text)

        list_person = tree.xpath('//default:teiHeader'
                                 '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=NAMESPACES)

        if not list_person:
            tree = self.__create_list_person(tree)
            list_person = tree.xpath('//default:teiHeader'
                                     '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=NAMESPACES)

        list_person[0].append(annotator)

        text = etree.tounicode(tree)

        return text

    @staticmethod
    def __create_list_person(tree):
        prefix = "{%s}" % NAMESPACES['default']

        ns_map = {
            None: NAMESPACES['default']
        }

        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)

        if not profile_desc:
            tei_header = tree.xpath('//default:teiHeader', namespaces=NAMESPACES)
            profile_desc = etree.Element(prefix + 'profileDesc', nsmap=ns_map)
            tei_header[0].append(profile_desc)

        partic_desc = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc', namespaces=NAMESPACES)

        if not partic_desc:
            profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)
            partic_desc = etree.Element(prefix + 'particDesc', nsmap=ns_map)
            profile_desc[0].append(partic_desc)

        list_person = tree.xpath(
            '//default:teiHeader/default:profileDesc/default:particDesc/default:listPerson[@type="PROVIDEDH Annotators"]',
            namespaces=NAMESPACES)

        if not list_person:
            partic_desc = tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc',
                                     namespaces=NAMESPACES)
            list_person = etree.Element(prefix + 'listPerson', type="PROVIDEDH Annotators", nsmap=ns_map)
            partic_desc[0].append(list_person)

        return tree

    def __add_certainty(self, text, certainty):
        tree = etree.fromstring(text)

        certainties = tree.xpath('//default:teiHeader'
                                 '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                 namespaces=NAMESPACES)

        if not certainties:
            tree = self.__create_annotation_list(tree)
            certainties = tree.xpath('//default:teiHeader'
                                     '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                     namespaces=NAMESPACES)

        certainties[0].append(certainty)

        text = etree.tounicode(tree)

        return text

    @staticmethod
    def __create_annotation_list(tree):
        default_namespace = NAMESPACES['default']
        default = "{%s}" % default_namespace

        ns_map = {
            None: default_namespace
        }

        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)

        if not profile_desc:
            tei_header = tree.xpath('//default:teiHeader', namespaces=NAMESPACES)
            profile_desc = etree.Element(default + 'profileDesc', nsmap=ns_map)
            tei_header[0].append(profile_desc)

        text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=NAMESPACES)

        if not text_class:
            profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)
            text_class = etree.Element(default + 'textClass', nsmap=ns_map)
            profile_desc[0].append(text_class)

        class_code = tree.xpath(
            '//default:teiHeader/default:profileDesc/default:textClass/default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
            namespaces=NAMESPACES)

        if not class_code:
            text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=NAMESPACES)
            class_code = etree.Element(default + 'classCode', scheme="http://providedh.eu/uncertainty/ns/1.0",
                                       nsmap=ns_map)
            text_class[0].append(class_code)

        return tree

    @staticmethod
    def __reformat_xml(text):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(text, parser=parser)
        pretty_xml = etree.tounicode(tree, pretty_print=True)

        return pretty_xml
