import logging
import re

from lxml import etree

from django.contrib.auth.models import User
from django.db.models import Q

from apps.api_vis.helpers import get_entity_from_int_or_dict, create_clique
from apps.api_vis.models import Entity, Certainty, Unification
from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import FileMaxXmlIds, File
from apps.projects.helpers import get_ana_link
from apps.projects.models import ProjectVersion


logger = logging.getLogger(__name__)

NAMESPACES = {
    'default': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xi': 'http://www.w3.org/2001/XInclude',
}

POSITION_PARAMS_V1 = [
    'start_row',
    'start_col',
    'end_row',
    'end_col',
]

POSITION_PARAMS_V2 = [
    'start_pos',
    'end_pos',
]


class Annotator:
    def __init__(self):
        self.__xml = ""
        self.__file = None
        self.__request = {}
        self.__annotator_xml_id = ""

        self.__target = False
        self.__target_in_db = False
        self.__positions = False
        self.__reference = False
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
        self.__list_element_to_add = None

        self.__xml_annotated = ""

    def add_annotation(self, xml, file_id, request, annotator_guid):
        self.__xml = xml
        self.__file = File.objects.get(id=file_id)
        self.__annotator_xml_id = 'person' + str(annotator_guid)

        self.__validate_request(request)
        self.__get_data_from_xml()
        self.__prepare_xml_parts()

        if self.__target_in_db:
            self.__check_if_new_elements_already_exist_in_db()
            self.__create_new_certainty_in_db()

            return self.__xml

        else:
            self.__check_if_new_elements_already_exist_in_xml()
            self.__create_new_xml()

            return self.__xml_annotated

    def __validate_request(self, request):

        # TODO: Delete after fix issue #47
        if 'attribute-name' in request:
            correction = {'attribute_name': request['attribute-name']}
            request.update(correction)

        self.__check_target_in_request(request)
        self.__check_positions_in_request(request)
        self.__check_reference_to_list_in_request(request)

        if self.__target and self.__positions:
            raise BadRequest("Provided reference parameters are ambiguous. Provide 'target' parameter for reference to "
                             "xml element, OR set of positional parameters for reference to text fragment.")

        if not self.__target and not self.__positions:
            raise BadRequest("Reference parameters not provided. Provide 'target' parameter for reference to "
                             "xml element, OR set of positional parameters for reference to text fragment.")

        if self.__target:
            self.__validate_target(request)
        elif self.__positions:
            self.__validate_positions(request)

        if self.__reference:
            self.__validate_list_element_id(request)

        self.__fill_in_optional_params(request)
        # self.__validate_closed_list_parameters() # TODO rewrite validation in suitable way

    def __check_target_in_request(self, request):
        if 'target' in request:
            self.__target = True

    def __check_positions_in_request(self, request):
        position_v1 = all(elements in request.keys() for elements in POSITION_PARAMS_V1)
        position_v2 = all(elements in request.keys() for elements in POSITION_PARAMS_V2)

        if position_v1 or position_v2:
            self.__positions = True

    def __check_reference_to_list_in_request(self, request):
        xml_id_regex = r'object_[\w]+-[\d]+'
        if 'asserted_value' in request and re.match(xml_id_regex, request['asserted_value']):
            self.__reference = True

    def __validate_target(self, request):
        text_in_lines = self.__xml.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = self.__xml

        tree = etree.fromstring(text_to_parse)
        annotation_ids = self.__get_annotation_ids_from_target(request['target'])

        for xml_id in annotation_ids:
            matching_xml_element = tree.xpath(f'//*[@xml:id="{xml_id}"]')

            user_id = int(self.__annotator_xml_id.replace('person', ''))

            matching_unification = Unification.objects.filter(
                (Q(created_in_commit__isnull=True) & Q(created_by_id=user_id))
                | Q(created_in_commit__isnull=False),
                entity__file=self.__file,
                xml_id=xml_id,
                deleted_on__isnull=True,
            ).distinct()

            if not matching_xml_element and not matching_unification:
                raise BadRequest(f"There is no element with xml:id: {xml_id} in file with id: {self.__file.id}")

            if matching_unification:
                self.__target_in_db = True

        self.__request.update({'target': request['target']})

    def __validate_list_element_id(self, request):
        text_in_lines = self.__xml.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_parse = '\n'.join(text_in_lines[1:])
        else:
            text_to_parse = self.__xml

        tree = etree.fromstring(text_to_parse)
        list_element_id = request['asserted_value']

        matching_xml_element = tree.xpath(f'//*[@xml:id="{list_element_id}"]', namespaces=NAMESPACES)

        if not matching_xml_element:
            raise BadRequest(f"There is no element with xml:id: {list_element_id} on any list in file "
                             f"with id: {self.__file.id}.")

    def __validate_positions(self, request):
        position_v1 = all(elements in request.keys() for elements in POSITION_PARAMS_V1)

        positions_to_check = POSITION_PARAMS_V1 if position_v1 else POSITION_PARAMS_V2

        for position in positions_to_check:
            if not isinstance(request[position], int):
                raise BadRequest(f"Value of '{position}' is not a integer.")

            if request[position] <= 0:
                raise BadRequest(f"Value of '{position}' must be a positive number.")

        validated_positions = {}

        if position_v1:
            start, end = self.__get_fragment_position(self.__xml, request)

            validated_positions.update({'start_pos': start, 'end_pos': end})
        else:
            validated_positions.update({'start_pos': request['start_pos'], 'end_pos': request['end_pos']})

        if validated_positions['start_pos'] >= validated_positions['end_pos']:
            raise BadRequest("Start position of annotating fragment is greater or equal to end position.")

        self.__request.update(validated_positions)

    def __fill_in_optional_params(self, request):
        optional_params = [
            'categories',
            'locus',
            'certainty',
            'asserted_value',
            'description',
            'tag',
            'attribute_name',
        ]

        filled_params = {}

        for param in optional_params:
            if param in request and request[param] is not None:
                filled_params.update({param: request[param]})
            else:
                filled_params.update({param: ''})

        self.__request.update(filled_params)

    def __validate_closed_list_parameters(self):
        correct_values = {
            'category': ['ignorance', 'credibility', 'imprecision', 'incompleteness'],
            'locus': ['value', 'name'],
            'certainty': ['unknown', 'very low', 'low', 'medium', 'high', 'very high'],
        }

        for parameter, values in correct_values.items():
            if self.__request[parameter] != '' and self.__request[parameter] not in values:
                values = [f"'{value}'" for value in values]
                values = ', '.join(values)

                raise BadRequest(f"Value of '{parameter}' parameter is incorrect. Correct values are: {values}.")

    def __get_data_from_xml(self):
        if self.__positions:
            self.__start, self.__end = self.__get_fragment_position(self.__xml, self.__request)
            self.__start, self.__end = self.__get_fragment_position_without_adhering_tags(self.__xml, self.__start,
                                                                                          self.__end)
            self.__start, self.__end = self.__get_fragment_position_with_adhering_tags(self.__xml, self.__start,
                                                                                       self.__end)
            self.__fragment_to_annotate = self.__xml[self.__start: self.__end]
            self.__tags = self.__get_adhering_tags_from_annotated_fragment(self.__fragment_to_annotate)

        self.__annotators_xml_ids = self.__get_annotators_xml_ids_from_file(self.__xml)
        certainties = self.__get_certainties_from_file(self.__xml)
        self.__tag_xml_id_number = self.__get_xml_id_number_for_tag(certainties, self.__request["tag"])
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
        if tag in ['event', 'org', 'person', 'place', 'certainty', 'object']:
            xml_id = self.__get_max_xml_id_from_database(tag)

            return xml_id

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
                    number = value.split('-')[-1]
                    number = int(number)

                    if number > biggest_number:
                        biggest_number = number

            return biggest_number + 1

    def __get_max_xml_id_from_database(self, tag):
        file_mx_xml_id = FileMaxXmlIds.objects.get(file=self.__file)

        file_mx_xml_id.__dict__[tag] += 1
        file_mx_xml_id.save()

        return file_mx_xml_id.__dict__[tag]

    def __prepare_xml_parts(self):
        # 1.Add tag to text
        if self.__request['locus'] == '' \
                and self.__request['tag'] != '' \
                and self.__request['attribute_name'] == '' \
                and self.__positions:
            self.__fragment_annotated, _ = self.__add_tag(self.__fragment_to_annotate, self.__request["tag"])

        # 2.Add certainty without tag to text
        elif self.__request['locus'] == 'value' \
                and self.__request['tag'] == '' \
                and self.__request['attribute_name'] == '' \
                and (self.__target or self.__positions):
            if self.__target:
                annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])
                annotation_ids = self.add_hash_sing_to_ids(annotation_ids)
            else:
                self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, 'ab',
                                                                           uncertainty=True)

            self.__certainty_to_add = self.__create_certainty_description(self.__request, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 3.Add certainty with tag to text
        elif self.__request['locus'] == 'value' \
                and self.__request['tag'] != '' \
                and self.__request['attribute_name'] == '' \
                and (self.__target or self.__positions):
            if self.__target:
                annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])
                annotation_ids = self.add_hash_sing_to_ids(annotation_ids)
            else:
                self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                           self.__request["tag"], uncertainty=True)

            self.__certainty_to_add = self.__create_certainty_description(self.__request, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        # 4.Add certainty to tag
        elif self.__request['locus'] == 'name' \
                and self.__request['tag'] != '' \
                and self.__request['attribute_name'] == '' \
                and (self.__target or self.__positions):
            if self.__target:
                annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])
                annotation_ids = self.add_hash_sing_to_ids(annotation_ids)
            else:
                self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                           self.__request["tag"], uncertainty=True)

            self.__certainty_to_add = self.__create_certainty_description(self.__request, annotation_ids,
                                                                          self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

            if self.__request['tag'] not in self.__tags and self.__request['asserted_value'] != '':
                raise BadRequest("You can't add asserted value for tag name when you creating new tag.")

        # 5.Add reference to tag
        elif self.__request['locus'] == 'value' \
                and self.__request['tag'] != '' \
                and self.__request['attribute_name'] == 'sameAs' \
                and self.__request['asserted_value'] != '' \
                and (self.__target or self.__positions):
            if self.__target:
                annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])
                annotation_ids = self.add_hash_sing_to_ids(annotation_ids)
            else:
                self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                           self.__request["tag"], uncertainty=True)

            self.__create_unification(annotation_ids)

        # 7.Add reference to element of the list
        elif self.__request['locus'] == 'value' \
                and self.__request['tag'] != '' \
                and self.__request['attribute_name'] == 'ref' \
                and self.__request['asserted_value'] != '' \
                and (self.__target or self.__positions):
            self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate, 'objectName',
                                                                       reference=True)

            self.__list_element_to_add = self.__create_list_element(self.__request, annotation_ids)

        # 6.Add attribute to tag
        elif self.__request['locus'] == 'value' \
                and self.__request['tag'] != '' \
                and self.__request['attribute_name'] != '' \
                and self.__request['asserted_value'] != '' \
                and (self.__target or self.__positions):
            if self.__target:
                annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])
                annotation_ids = self.add_hash_sing_to_ids(annotation_ids)
            else:
                self.__fragment_annotated, annotation_ids = self.__add_tag(self.__fragment_to_annotate,
                                                                           self.__request["tag"], uncertainty=True)

            self.__certainty_to_add = self.__create_certainty_description_for_attribute(self.__request, annotation_ids,
                                                                                        self.__annotator_xml_id)
            self.__annotator_to_add = self.__create_annotator(self.__annotator_xml_id)

        else:
            raise BadRequest("There is no method to modify xml according to given parameters.")

    def __add_tag(self, annotated_fragment, tag, uncertainty=False, reference=False):
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

                    if uncertainty:
                        if 'xml:id="' not in tag_to_move:
                            id = f"{tag}_{self.__file.name}-{self.__tag_xml_id_number}"
                            attribute = f' xml:id="{id}"'

                            annotation_ids.append('#' + id)

                            new_tag_to_move = tag_to_move[:len(tag_begin)] + attribute + tag_to_move[len(tag_begin):]

                            self.__tag_xml_id_number += 1
                        else:
                            match = re.search(r'xml:id=".*?"', tag_to_move)
                            existing_id = match.group()
                            existing_id = existing_id.replace('xml:id="', '')
                            existing_id = existing_id.replace('"', '')

                            annotation_ids.append('#' + existing_id)
                            new_tag_to_move = tag_to_move

                        new_annotated_fragment += new_tag_to_move

                    elif reference:
                        if 'ref="' not in tag_to_move:
                            id = self.__get_id_of_list_object_to_reference()
                            attribute = f' ref="#{id}"'

                            annotation_ids.append('#' + id)
                            new_tag_to_move = tag_to_move[:len(tag_begin)] + attribute + tag_to_move[len(tag_begin):]

                        else:
                            match = re.search(r'ref=".*?"', tag_to_move)
                            existing_reference = match.group()

                            id = self.__get_id_of_list_object_to_reference()

                            if id in existing_reference:
                                raise NotModified(f"Reference to element with xml:id: {id} already exist.")

                            updated_reference = f'{existing_reference[:-1]} #{id}"'

                            annotation_ids.append('#' + id)
                            new_tag_to_move = tag_to_move.replace(existing_reference, updated_reference)

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
                        attribute = f' xml:id="{id}"'

                        annotation_ids.append('#' + id)

                    elif reference:
                        id = self.__get_id_of_list_object_to_reference()
                        attribute = f' ref="#{id}"'

                        annotation_ids.append('#' + id)

                    tag_open = f'<{tag}{attribute}>'
                    tag_close = f'</{tag}>'

                    new_annotated_fragment += tag_open + text_to_move + tag_close

                    annotated_fragment = annotated_fragment[len(text_to_move):]

                    if uncertainty:
                        self.__tag_xml_id_number += 1

        return new_annotated_fragment, annotation_ids

    def __get_id_of_list_object_to_reference(self):
        xml_id_regex = r'object_[\w]+-[\d]+'
        if re.match(xml_id_regex, self.__request['asserted_value']):
            id = self.__request['asserted_value'].replace('#', '')

        else:
            xml_id_number = self.__get_max_xml_id_from_database('object')
            id = f"object_{self.__file.name}-{xml_id_number}"

        return id

    @staticmethod
    def __get_annotation_ids_from_target(target):
        if type(target) == list:

            return target

        elif type(target) == str:
            target = target.split(' ')

            return target

    @staticmethod
    def add_hash_sing_to_ids(ids):
        new_ids = []

        for id in ids:
            if id[0] != '#':
                id = '#' + id

            new_ids.append(id)

        return new_ids

    def __create_certainty_description(self, json, annotation_ids, user_uuid):
        target = " ".join(annotation_ids)
        xml_id = f"certainty_{self.__file.name}-{self.__certainty_xml_id_number}"

        categories = " ".join([get_ana_link(self.__file.project_id, cat) for cat in json["categories"]])
        certainty = f'<certainty ana="{categories}" locus="{json["locus"]}" cert="{json["certainty"]}" ' \
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

        categories = " ".join([get_ana_link(self.__file.project_id, cat) for cat in json["categories"]])
        certainty = f'<certainty ana="{categories}" locus="{json["locus"]}" cert="{json["certainty"]}" ' \
                    f'resp="#{user_uuid}" target="{target}" match="@{json["attribute_name"]}"' \
                    f'assertedValue="{json["asserted_value"]}" xml:id="{xml_id}"/>'

        new_element = etree.fromstring(certainty)

        if json["description"]:
            description = etree.Element("desc")
            description.text = json["description"]

            new_element.append(description)

        return new_element

    def __create_list_element(self, json, annotation_ids):
        xml_id = annotation_ids[0].replace('#', '')

        element = f'<object type="{self.__request["tag"]}" xml:id="{xml_id}">' \
                  f'{self.__request["asserted_value"]}</object>'

        new_element = etree.fromstring(element)

        return new_element

    def __create_annotator(self, user_xml_id):
        user_guid = user_xml_id.replace('person', '')

        annotator_data = self.__get_user_data_from_db(user_guid)

        annotator = f"""
            <person xml:id="{user_xml_id}">
              <persName>
                <forename>{annotator_data['forename']}</forename>
                <surname>{annotator_data['surname']}</surname>
                <email>{annotator_data['email']}</email>
              </persName>
              <link>{annotator_data['link']}</link>
            </person>
        """

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

    def __check_if_new_elements_already_exist_in_db(self):
        certainty = self.__certainty_to_add.attrib
        desc = self.__certainty_to_add.xpath('.//desc', namespaces=NAMESPACES)

        user_id = int(self.__annotator_xml_id.replace('person', ''))
        annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])

        if len(annotation_ids) > 1:
            raise BadRequest('Add certainty to more than one certainty is not allowed.')

        unification = Unification.objects.get(
            (Q(created_in_commit__isnull=True) & Q(created_by_id=user_id))
            | Q(created_in_commit__isnull=False),
            entity__file=self.__file,
            xml_id=annotation_ids[0],
            deleted_on__isnull=True,
        )

        certainties = Certainty.objects.filter(
            ana=certainty['ana'],
            locus=certainty['locus'],
            cert=certainty['cert'],
            asserted_value=certainty['assertedValue'] if 'assertedValue' in certainty else None,
            target=certainty['target'],
            description=desc[0].text if desc else None,
            unification=unification,
        )

        if len(certainties) > 0:
            raise NotModified('This certainty already exist.')

    def __check_if_new_elements_already_exist_in_xml(self):
        if self.__request['locus'] == '' and self.__request['tag'] in self.__tags:
            raise NotModified('This tag already exist.')

        if self.__certainty_to_add is not None:
            xml = self.__xml

            xml_in_lines = xml.splitlines()
            if 'encoding=' in xml_in_lines[0]:
                xml = '\n'.join(xml_in_lines[1:])

            tree = etree.fromstring(xml)
            xpath = f'//default:teiHeader' \
                    f'//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]' \
                    f'//default:certainty[@ana="{self.__certainty_to_add.attrib["ana"]}" ' \
                    f'and @locus="{self.__certainty_to_add.attrib["locus"]}" ' \
                    f'and @cert="{self.__certainty_to_add.attrib["cert"]}" ' \
                    f'and @target="{self.__certainty_to_add.attrib["target"]}"'

            if self.__request['asserted_value']:
                xpath += f' and @assertedValue="{self.__request["asserted_value"]}"'

            xpath += ']'

            existing_certainties = tree.xpath(xpath, namespaces=NAMESPACES)

            if existing_certainties and self.__request['description']:
                descriptions = tree.xpath(xpath + '/default:desc', namespaces=NAMESPACES)

                for desc in descriptions:
                    if desc.text == self.__request['description']:
                        raise NotModified('This certainty already exist.')

            elif existing_certainties and not self.__request['description']:
                raise NotModified('This certainty already exist.')

        if not self.__reference and self.__request['attribute_name'] == 'ref' and self.__request['locus'] == 'value':
            xml = self.__xml

            xml_in_lines = xml.splitlines()
            if 'encoding=' in xml_in_lines[0]:
                xml = '\n'.join(xml_in_lines[1:])

            tree = etree.fromstring(xml)
            xpath = f'//default:text' \
                    f'//default:body' \
                    f'//default:div[@type="{self.__request["tag"]}"]' \
                    f'//default:listObject' \
                    f'//default:object[@type="{self.__request["tag"]}" and text()="{self.__request["asserted_value"]}"]'

            existing_element = tree.xpath(xpath, namespaces=NAMESPACES)

            if existing_element:
                xml_namespace = NAMESPACES['xml']
                xml = '{%s}' % xml_namespace

                xml_id = existing_element[0].attrib[etree.QName(xml + 'id')]

                raise BadRequest(f"Item: {self.__request['asserted_value']} already exist on: "
                                 f"{self.__request['tag']} list and have id: {xml_id}")

    def __create_new_certainty_in_db(self):
        certainty = self.__certainty_to_add.attrib
        desc = self.__certainty_to_add.xpath('.//desc', namespaces=NAMESPACES)
        prefix = '{%s}' % NAMESPACES['xml']

        user_id = int(self.__annotator_xml_id.replace('person', ''))
        xml_id = certainty[prefix + 'id']

        annotation_ids = self.__get_annotation_ids_from_target(self.__request['target'])

        unification = Unification.objects.get(
            (Q(created_in_commit__isnull=True) & Q(created_by_id=user_id))
            | Q(created_in_commit__isnull=False),
            entity__file=self.__file,
            xml_id=annotation_ids[0],
            deleted_on__isnull=True,
        )

        Certainty.objects.create(
            ana=certainty['ana'],
            locus=certainty['locus'],
            cert=certainty['cert'],
            asserted_value=certainty['assertedValue'] if 'assertedValue' in certainty else None,
            resp=certainty['resp'],
            target=certainty['target'],
            xml_id=certainty[prefix + 'id'],
            description=desc[0].text if desc else None,
            unification=unification,
        )

    def __create_new_xml(self):
        xml_annotated = self.__add_tagged_string(self.__xml, self.__fragment_annotated)

        xml_annotated_in_lines = xml_annotated.splitlines()
        if 'encoding=' in xml_annotated_in_lines[0]:
            xml_annotated = '\n'.join(xml_annotated_in_lines[1:])

        if self.__annotator_xml_id not in self.__annotators_xml_ids and self.__annotator_to_add is not None:
            xml_annotated = self.__add_annotator(xml_annotated, self.__annotator_to_add)

        if self.__certainty_to_add is not None:
            xml_annotated = self.__add_certainty(xml_annotated, self.__certainty_to_add)

        if self.__list_element_to_add is not None:
            xml_annotated = self.__add_list_element(xml_annotated, self.__list_element_to_add)
            xml_annotated = self.__reorder_elements(xml_annotated)

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

    def __add_list_element(self, text, element):
        tree = etree.fromstring(text)
        element_type = element.get('type')
        list_xpath = f'/default:TEI/default:text/default:body/default:div[@type="{element_type}"]/default:listObject'

        list = tree.xpath(list_xpath, namespaces=NAMESPACES)

        if not list:
            tree = self.__create_elements_from_xpath(tree, list_xpath)
            list = tree.xpath(list_xpath, namespaces=NAMESPACES)

        list[0].append(element)

        text = etree.tounicode(tree)

        return text

    @staticmethod
    def __create_elements_from_xpath(tree, xpath):
        default_namespace = NAMESPACES['default']

        ns_map = {
            None: default_namespace
        }

        path_steps = xpath.split('/')
        path_steps = [step for step in path_steps if step != '']

        for i in range(len(path_steps)):
            i += 1

            element_xpath = '/' + '/'.join(path_steps[:i])
            element = tree.xpath(element_xpath, namespaces=NAMESPACES)

            if not element:
                parent_xpath = '/' + '/'.join(path_steps[:i-1])
                parent = tree.xpath(parent_xpath, namespaces=NAMESPACES)

                step = path_steps[i-1]

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

                namespace = '{%s}' % NAMESPACES[prefix]

                element = etree.Element(namespace + name, nsmap=ns_map)

                if attributes_dict:
                    for key, value in attributes_dict.items():
                        element.set(key, value)

                parent[0].append(element)

        return tree

    @staticmethod
    def __reorder_elements(text):
        parent_xpath = f'/default:TEI/default:text/default:body'

        # TODO: Hardcoded order for workshop with recipes. During generalization change this to use types selected
        #  by user
        order = ['ingredient', 'utensil', 'dietetic', 'productionMethod', 'recipe']

        tree = etree.fromstring(text)
        parent = tree.xpath(parent_xpath, namespaces=NAMESPACES)[0]
        children_queue = []

        for type in order:
            children = parent.findall(f'default:div[@type="{type}"]', namespaces=NAMESPACES)
            children_queue += children

            for child in children:
                parent.remove(child)

        for child in reversed(children_queue):
            parent.insert(0, child)

        text = etree.tounicode(tree)

        return text

    @staticmethod
    def __reformat_xml(text):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(text, parser=parser)
        pretty_xml = etree.tounicode(tree, pretty_print=True)

        return pretty_xml

    def __create_unification(self, annotation_ids):
        if len(annotation_ids) > 1:
            raise BadRequest("Entity to unify must have only one xml:id.")

        try:
            entity = Entity.objects.get(
                project_id=self.__file.project_id,
                file=self.__file,
                xml_id=annotation_ids[0].replace('#', ''),
                deleted_on__isnull=True,
            )
        except Entity.DoesNotExist:
            raise BadRequest("This entity doesn't exist in database. "
                             "Add tag to marked text, save file and try again.")

        entities_ids = [entity.id]

        project_id = self.__file.project_id
        asserted_entities = self.__request['asserted_value'].split(' ')

        for asserted_entity in asserted_entities:
            if '#' not in asserted_entity:
                entity = Entity.objects.filter(
                    project_id=self.__file.project_id,
                    file=self.__file,
                    xml_id=asserted_entity,
                    deleted_on__isnull=True,
                )

                entities_ids.append(entity.id)
            else:
                entity_dict = {
                    'file_path': asserted_entity.split('#')[0],
                    'xml_id': asserted_entity.split('#')[1],
                }

                entity = get_entity_from_int_or_dict(entity_dict, project_id)

                entities_ids.append(entity.id)

        project_version = ProjectVersion.objects.filter(
            project_id=project_id
        ).order_by('-date')[0]

        request_data = {
            'entities': entities_ids,
            'certainty': self.__request['certainty'],
            'project_version': float(str(project_version)),
        }

        user_id = int(self.__annotator_xml_id.replace('person', ''))
        user = User.objects.get(id=user_id)

        create_clique(request_data, project_id, user)
