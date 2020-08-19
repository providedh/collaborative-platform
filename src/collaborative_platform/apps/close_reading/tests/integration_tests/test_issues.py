import inspect
import json
import os
import pytest

from apps.api_vis.models import EntityProperty
from apps.close_reading.tests.integration_tests.test_annotator_with_ws_and_db import get_communicator, read_file


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue111:
    """Unsaved uncertainty annotations are not correctly deleted"""

    async def test_forbid_deleting_unsaved_tag(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 265,
                        'end_pos': 271,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'tag',
                    'edited_element_id': 'ab-1'
                }
            ]
        }

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()

        assert response['status'] == 400
        assert response['message'] == "Deleting an unsaved element is forbidden. Instead of deleting, discard " \
                                      "the operation that created this element."

        await communicator.disconnect()

    async def test_forbid_deleting_unsaved_reference(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 265,
                        'end_pos': 271,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'new_element_id': 'person-2'
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'old_element_id': 'person-2',
                }
            ]
        }

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()

        assert response['status'] == 400
        assert response['message'] == "Deleting an unsaved element is forbidden. Instead of deleting, discard " \
                                      "the operation that created this element."

        await communicator.disconnect()

    async def test_forbid_deleting_unsaved_property(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-0',
                    'parameters': {
                        'forename': 'Bruce'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-0',
                    'old_element_id': 'forename'
                }
            ]
        }

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()

        assert response['status'] == 400
        assert response['message'] == "Deleting an unsaved element is forbidden. Instead of deleting, discard " \
                                      "the operation that created this element."

        await communicator.disconnect()

    async def test_forbid_deleting_unsaved_certainty(self):
        """Case replicated from issue description"""

        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'ab-0',
                    'parameters': {
                        'categories': ['imprecision'],
                        'locus': 'value',
                        'certainty': 'medium',
                        'asserted_value': 'oven'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-5',
                }
            ]
        }

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()

        assert response['status'] == 400
        assert response['message'] == "Deleting an unsaved element is forbidden. Instead of deleting, discard " \
                                      "the operation that created this element."

        await communicator.disconnect()


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue112:
    """Unsaved annotations are not correctly modified"""

    async def test_move_unsaved_tag_to_new_position(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 265,
                        'end_pos': 271,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'start_pos': 251,
                        'end_pos': 336,
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_modify_unsaved_property(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 265,
                        'end_pos': 271,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                        'entity_properties': {
                            'name': 'new date'
                        }
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_properties = EntityProperty.objects.filter(
            entity_version__entity__file_id=file_id,
            entity_version__entity__xml_id='date-3',
            name='when'
        )
        assert entity_properties.count() == 0

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-3',
                    'parameters': {
                        'when': '2020-02-02'
                    }
                }
            ]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_properties = EntityProperty.objects.filter(
            entity__file_id=file_id,
            entity__xml_id='date-3',
            name='when'
        )
        assert entity_properties.count() == 1

        entity_property = entity_properties[0]
        assert entity_property.get_value(as_str=True) == '2020-02-02'

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-3',
                    'old_element_id': 'when',
                    'parameters': {
                        'when': '1001-01-01'
                    }
                }
            ]
        }
        request_nr = 3

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_properties = EntityProperty.objects.filter(
            entity__file_id=file_id,
            entity__xml_id='date-3',
            name='when'
        )
        assert entity_properties.count() == 1

        entity_property = entity_properties[0]
        assert entity_property.get_value(as_str=True) == '1001-01-01'

        await communicator.disconnect()

    async def test_modify_unsaved_certainty(self):
        """Case replicated from issue description"""

        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'ab-0',
                    'parameters': {
                        'categories': ['imprecision'],
                        'locus': 'value',
                        'certainty': 'medium',
                        'asserted_value': 'oven'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    "method": "PUT",
                    "element_type": "certainty",
                    "edited_element_id": "certainty-5",
                    "old_element_id": "asserted_value",
                    'parameters': {
                        "asserted_value": "electric oven"
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()


def verify_response(test_name, response, request_nr):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results_for_issues.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)
    expected = test_results[test_name][request_nr]

    for field in expected.keys():
        assert response[field] == expected[field]
