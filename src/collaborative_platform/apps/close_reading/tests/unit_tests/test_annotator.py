# import json
# import os
# import pytest
#
# from django.contrib.auth.models import User
#
# from apps.close_reading.annotator import Annotator
# from apps.exceptions import BadRequest, NotModified
# from apps.files_management.helpers import create_certainty_elements_for_file_version, certainty_elements_to_json
# from apps.files_management.models import FileVersion
#
#
# SCRIPT_DIR = os.path.dirname(__file__)
#
#
# def read_file(path):
#     with open(path, 'r') as file:
#         text = file.read()
#
#     return text


# @pytest.mark.unit_tests
# class TestAnnotator:
#     @pytest.mark.django_db
#     def test_add_annotation__add_tag_to_text__fragment_without_tag__string(self):
#         request = {
#             'start_pos': 9710,
#             'end_pos': 9715,
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_tag_to_text__fragment_without_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_tag_to_text__fragment_with_other_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_tag_to_text__fragment_with_other_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_tag_to_text__fragment_with_same_tag__exception(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'tag': 'place',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(NotModified) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This tag already exist."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_tag_to_text__fragment_with_same_tag_and_certainty__exception(self):
#         request = {
#             'start_row': 222,
#             'start_col': 127,
#             'end_row': 222,
#             'end_col': 133,
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(NotModified) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This tag already exist."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_without_tag_to_text__fragment_without_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 7,
#             'end_row': 221,
#             'end_col': 11,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': '',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_without_tag_to_text__fragment_without_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_without_tag_to_text__fragment_with_other_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': '',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_without_tag_to_text__fragment_with_other_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_without_tag_to_text__fragment_with_same_tag_and_other_certainty__string(self):
#         request = {
#             'start_row': 222,
#             'start_col': 2070,
#             'end_row': 222,
#             'end_col': 2096,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': '',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_without_tag_to_text__fragment_with_same tag_and_other_certainty__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_without_tag_to_text__fragment_with_same_tag_and_same_certainty__exception(self):
#         request = {
#             'start_row': 222,
#             'start_col': 2070,
#             'end_row': 222,
#             'end_col': 2096,
#             'categories': ['credibility'],
#             'locus': 'value',
#             'certainty': 'low',
#             'asserted_value': '',
#             'description': '',
#             'tag': '',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(NotModified) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This certainty already exist."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_with_tag_to_text__fragment_without_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 7,
#             'end_row': 221,
#             'end_col': 11,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_with_tag_to_text__fragment_without_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_with_tag_to_text__fragment_with_other_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_with_tag_to_text__fragment_with_other_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_with_tag_to_text__fragment_with_same_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'place',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_with_tag_to_text__fragment_with_same_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_with_tag_to_text__fragment_with_same_tag_and_other_certainty__string(self):
#         request = {
#             'start_row': 222,
#             'start_col': 127,
#             'end_row': 222,
#             'end_col': 133,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'asserted_value': 'November',
#             'description': 'awesome description',
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_with_tag_to_text__fragment_with_same_tag_and_other_certainty__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_with_tag_to_text__fragment_with_same_tag_and_same_certainty__exception(self):
#         request = {
#             'start_row': 221,
#             'start_col': 501,
#             'end_row': 221,
#             'end_col': 519,
#             'categories': ['imprecision'],
#             'locus': 'value',
#             'certainty': 'medium',
#             'asserted_value': 'Dublin',
#             'description': '',
#             'tag': 'country',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(NotModified) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This certainty already exist."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_to_tag__fragment_without_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 7,
#             'end_row': 221,
#             'end_col': 11,
#             'categories': ['ignorance'],
#             'locus': 'name',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'org',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_to_tag__fragment_without_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_to_tag__fragment_with_other_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'categories': ['ignorance'],
#             'locus': 'name',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'org',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_to_tag__fragment_with_other_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_to_tag__fragment_with_same_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'categories': ['ignorance'],
#             'locus': 'name',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'place',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_to_tag__fragment_with_same_tag__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_to_tag__fragment_with_same_tag_and_other_certainty__string(self):
#         request = {
#             'start_row': 222,
#             'start_col': 127,
#             'end_row': 222,
#             'end_col': 133,
#             'categories': ['ignorance'],
#             'locus': 'name',
#             'certainty': 'high',
#             'asserted_value': 'person',
#             'description': 'awesome description',
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#         expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                           'add_certainty_to_tag__fragment_with_same_tag_and_other_certainty__result.xml')
#
#         input_text = read_file(input_file_path)
#         expected_text = read_file(expected_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == expected_text
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_to_tag__fragment_with_same_tag_and_same_certainty__exception(self):
#         request = {
#             'start_row': 222,
#             'start_col': 127,
#             'end_row': 222,
#             'end_col': 133,
#             'categories': ['credibility'],
#             'locus': 'name',
#             'certainty': 'high',
#             'asserted_value': '',
#             'description': '',
#             'tag': 'date',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(NotModified) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This certainty already exist."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_certainty_to_tag__add_new_tag_with_asserted_value_for_name__exception(self):
#         request = {
#             'start_row': 221,
#             'start_col': 7,
#             'end_row': 221,
#             'end_col': 11,
#             'categories': ['credibility'],
#             'locus': 'name',
#             'certainty': 'high',
#             'asserted_value': 'place',
#             'description': '',
#             'tag': 'place',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(BadRequest) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "You can't add asserted value for tag name when you creating new tag."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_reference_to_tag__fragment_without_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 7,
#             'end_row': 221,
#             'end_col': 11,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'attribute_name': 'sameAs',
#             'asserted_value': '#person_source_file_xml-18',
#             'description': '',
#             'tag': 'person',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(BadRequest) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This entity doesn't exist in database. Add tag to marked text, save file and " \
#                                        "try again."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_reference_to_tag__fragment_with_other_tag__string(self):
#         request = {
#             'start_row': 221,
#             'start_col': 106,
#             'end_row': 221,
#             'end_col': 125,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'attribute_name': 'sameAs',
#             'asserted_value': 'person_source_file_xml-18',
#             'description': '',
#             'tag': 'person',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         with pytest.raises(BadRequest) as exception:
#             annotator = Annotator()
#             result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert str(exception.value) == "This entity doesn't exist in database. Add tag to marked text, save file and " \
#                                        "try again."
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_reference_to_tag__fragment_with_same_tag__string(self):
#         request = {
#             'start_row': 230,
#             'start_col': 190,
#             'end_row': 230,
#             'end_col': 200,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'attribute_name': 'sameAs',
#             'asserted_value': '#person_source_file_xml-14',
#             'description': '',
#             'tag': 'person',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == input_text
#
#         file_version = FileVersion.objects.get(file_id=file_id, number=2)
#         user = User.objects.get(id=user_id)
#
#         certainty_elements = create_certainty_elements_for_file_version(file_version, include_uncommitted=True,
#                                                                         user=user, for_annotator=True)
#         certainties_from_db = certainty_elements_to_json(certainty_elements)
#
#         expected_certainties = [
#             {
#                 'certainty': {
#                     '@ana': '',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-15',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-13',
#                     '@xml:id': 'certainty_source_file_xml-16'
#                 },
#                 'committed': True
#             },
#             {
#                 'certainty': {
#                     '@ana': '',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-13',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-15',
#                     '@xml:id': 'certainty_source_file_xml-15'
#                 },
#                 'committed': True
#             },
#             {
#                 'certainty': {
#                     '@ana': 'https://providedh.ehum.psnc.pl/api/projects/1/taxonomy/#ignorance',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-14',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-18',
#                     '@xml:id': 'certainty_source_file_xml-19',
#                 },
#                 'committed': False,
#             },
#             {
#                 'certainty': {
#                     '@ana': 'https://providedh.ehum.psnc.pl/api/projects/1/taxonomy/#ignorance',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-18',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-14',
#                     '@xml:id': 'certainty_source_file_xml-18',
#                 },
#                 'committed': False,
#             }
#         ]
#
#         result_certainties = json.loads(certainties_from_db)
#
#         assert result_certainties == expected_certainties
#
#     @pytest.mark.django_db
#     def test_add_annotation__add_reference_to_tag__fragment_with_same_tag_and_other_certainty__string(self):
#         request = {
#             'start_row': 222,
#             'start_col': 423,
#             'end_row': 222,
#             'end_col': 434,
#             'categories': ['ignorance'],
#             'locus': 'value',
#             'certainty': 'high',
#             'attribute_name': 'sameAs',
#             'asserted_value': '#person_source_file_xml-14',
#             'description': 'awesome description',
#             'tag': 'person',
#         }
#
#         input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#         input_text = read_file(input_file_path)
#
#         user_id = 2
#         file_id = 1
#
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, request, user_id)
#
#         assert result == input_text
#
#         file_version = FileVersion.objects.get(file_id=file_id, number=2)
#         user = User.objects.get(id=user_id)
#
#         certainty_elements = create_certainty_elements_for_file_version(file_version, include_uncommitted=True,
#                                                                         user=user, for_annotator=True)
#         certainties_from_db = certainty_elements_to_json(certainty_elements)
#
#         expected_certainties = [
#             {
#                 'certainty': {
#                     '@ana': '',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-15',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-13',
#                     '@xml:id': 'certainty_source_file_xml-16',
#                 },
#                 'committed': True,
#             },
#             {
#                 'certainty': {
#                     '@ana': '',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-13',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-15',
#                     '@xml:id': 'certainty_source_file_xml-15',
#                 },
#                 'committed': True,
#             },
#             {
#                 'certainty': {
#                     '@ana': 'https://providedh.ehum.psnc.pl/api/projects/1/taxonomy/#ignorance',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-14',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-13',
#                     '@xml:id': 'certainty_source_file_xml-19',
#                     'desc': 'awesome description',
#                 },
#                 'committed': False,
#             },
#             {
#                 'certainty': {
#                     '@ana': 'https://providedh.ehum.psnc.pl/api/projects/1/taxonomy/#ignorance',
#                     '@locus': 'value',
#                     '@cert': 'high',
#                     '@resp': '#person2',
#                     '@target': '#person_source_file_xml-13',
#                     '@match': '@sameAs',
#                     '@assertedValue': '#person_source_file_xml-14',
#                     '@xml:id': 'certainty_source_file_xml-18',
#                     'desc': 'awesome description',
#                 },
#                 'committed': False,
#             }
#         ]
#
#         result_certainties = json.loads(certainties_from_db)
#
#         assert result_certainties == expected_certainties

#     TODO: Enable this test after add checking if unification from request already exist in database
#     @pytest.mark.django_db
#     def test_add_annotation__add_reference_to_tag__fragment_with_same_tag_and_same_certainty__exception(self):
#         json = {
#             'start_row': 222,
#             'start_col': 648,
#             'end_row': 222,
#             'end_col': 674,
#             'categories': [],
#             'locus': 'value',
#             'certainty': 'high',
#             'attribute_name': 'sameAs',
#             'asserted_value': '#person_source_file_xml-13',
#             'description': '',
#             'tag': 'person',
#         }
#
#     input_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', 'source_file.xml')
#
#     input_text = read_file(input_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     with pytest.raises(NotModified) as exception:
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#         assert exception.exception.message == "This certainty already exist."

# @pytest.mark.django_db
# def test_add_annotation__add_attribute_to_tag__fragment_without_tag__string(self):
#     json = {
#         'start_row': 221,
#         'start_col': 7,
#         'end_row': 221,
#         'end_col': 11,
#         'categories': ['ignorance'],
#         'locus': 'value',
#         'certainty': 'high',
#         'attribute_name': 'sex',
#         'asserted_value': 'female',
#         'description': '',
#         'tag': 'person',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'add_attribute_to_tag__fragment_without_tag__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# @pytest.mark.django_db
# def test_add_annotation__add_attribute_to_tag__fragment_with_other_tag__string(self):
#     json = {
#         'start_row': 221,
#         'start_col': 106,
#         'end_row': 221,
#         'end_col': 125,
#         'categories': ['ignorance'],
#         'locus': 'value',
#         'certainty': 'high',
#         'attribute_name': 'sex',
#         'asserted_value': 'female',
#         'description': '',
#         'tag': 'person',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'add_attribute_to_tag__fragment_with_other_tag__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# @pytest.mark.django_db
# def test_add_annotation__add_attribute_to_tag__fragment_with_same_tag__string(self):
#     json = {
#         'start_row': 222,
#         'start_col': 504,
#         'end_row': 222,
#         'end_col': 554,
#         'categories': ['ignorance'],
#         'locus': 'value',
#         'certainty': 'high',
#         'attribute_name': 'sex',
#         'asserted_value': 'male',
#         'description': '',
#         'tag': 'person',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'add_attribute_to_tag__fragment_with_same_tag__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# @pytest.mark.django_db
# def test_add_annotation__add_attribute_to_tag__fragment_with_same_tag_and_other_certainty__string(self):
#     json = {
#         'start_row': 222,
#         'start_col': 423,
#         'end_row': 222,
#         'end_col': 434,
#         'categories': ['credibility'],
#         'locus': 'value',
#         'certainty': 'high',
#         'attribute_name': 'sex',
#         'asserted_value': 'male',
#         'description': '',
#         'tag': 'person',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'add_attribute_to_tag__fragment_with_same_tag_and_other_certainty__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# @pytest.mark.django_db
# def test_add_annotation__add_attribute_to_tag__fragment_with_same_tag_and_same_certainty__exception(self):
#     json = {
#         'start_row': 222,
#         'start_col': 423,
#         'end_row': 222,
#         'end_col': 434,
#         'categories': ['ignorance'],
#         'locus': 'value',
#         'certainty': 'high',
#         'attribute_name': 'sex',
#         'asserted_value': 'male',
#         'description': '',
#         'tag': 'person',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#
#     input_text = read_file(input_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     with pytest.raises(NotModified) as exception:
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert str(exception.value) == "This certainty already exist."
#
# @pytest.mark.django_db
# def test_add_annotation__add_certainty_with_tag_to_text__fragment_with_same_tag_separated__string(self):
#     json = {
#         'start_row': 222,
#         'start_col': 504,
#         'end_row': 222,
#         'end_col': 554,
#         'categories': ['ignorance'],
#         'locus': 'value',
#         'certainty': 'high',
#         'asserted_value': '',
#         'description': '',
#         'tag': 'person',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'add_certainty_with_tag_to_text__fragment_with_same_tag_separated__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# @pytest.mark.django_db
# def test_add_annotation__add_first_annotator_and_certainty__string(self):
#     json = {
#         'start_row': 57,
#         'start_col': 7,
#         'end_row': 57,
#         'end_col': 11,
#         'categories': ['ignorance'],
#         'locus': 'value',
#         'certainty': 'high',
#         'asserted_value': '',
#         'description': '',
#         'tag': '',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file_without_annotators_and_certainties.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'add_first_annotator_and_certainty__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# @pytest.mark.django_db
# def test_add_annotation__position_in_request_with_adhering_tags__string(self):
#     json = {
#         'start_row': 231,
#         'start_col': 19,
#         'end_row': 231,
#         'end_col': 68,
#         'tag': 'date',
#     }
#
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'source_file.xml')
#     expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'result_files',
#                                       'position_in_request_with_adhering_tags__result.xml')
#
#     input_text = read_file(input_file_path)
#     expected_text = read_file(expected_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     annotator = Annotator()
#     result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert result == expected_text
#
# test_parameters_list = [
#     (
#         # Empty parameters
#         {
#             'start_row': 54,
#             'start_col': 7,
#             'end_row': 54,
#             'end_col': 11,
#             'category': '',
#             'locus': '',
#             'certainty': '',
#             'asserted_value': '',
#             'description': '',
#             'tag': '',
#         },
#         BadRequest,
#         "There is no method to modify xml according to given parameters.",
#     ),
#     (
#         # start_pos is greater than end_pos
#         {
#             'start_pos': 8440,
#             'end_pos': 8435,
#             'tag': 'test',
#         },
#         BadRequest,
#         "Start position of annotating fragment is greater or equal to end position.",
#     ),
#     (
#         # No position arguments
#         {
#             'tag': 'test',
#         },
#         BadRequest,
#         "Reference parameters not provided. Provide 'target' parameter for reference to xml element, OR set of "
#         "positional parameters for reference to text fragment.",
#     ),
#     (
#         # Position is not a integer
#         {
#             'start_row': 54.15,
#             'start_col': 7,
#             'end_row': 54,
#             'end_col': 11,
#             'tag': 'test',
#         },
#         BadRequest,
#         "Value of 'start_row' is not a integer."
#     ),
#     (
#         # Position is not a positive_number
#         {
#             'start_row': 54,
#             'start_col': -7,
#             'end_row': 54,
#             'end_col': 11,
#             'tag': 'test',
#         },
#         BadRequest,
#         "Value of 'start_col' must be a positive number."
#     ),
# ]
#
# test_parameters_names = "json, error_type, error_message"
#
# @pytest.mark.django_db
# @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
# def test_add_annotation__wrong_request_parameters__exception(self, json, error_type, error_message):
#     input_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files',
#                                    'source_file_without_annotators_and_certainties.xml')
#
#     input_text = read_file(input_file_path)
#
#     user_id = 2
#     file_id = 1
#
#     with pytest.raises(error_type) as exception:
#         annotator = Annotator()
#         result = annotator.add_annotation(input_text, file_id, json, user_id)
#
#     assert str(exception.value) == error_message
