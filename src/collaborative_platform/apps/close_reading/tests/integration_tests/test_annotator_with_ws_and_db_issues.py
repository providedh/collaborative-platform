import inspect
import json
import os
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Entity, EntityProperty
from apps.close_reading.tests.integration_tests.test_annotator_with_ws_and_db import get_communicator, read_file
from apps.files_management.models import Directory, File
from apps.files_management.tests.integration_tests.test_file_handling_with_hd_and_db import upload_file, download_file
from apps.projects.models import Project


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
                    'edited_element_id': 'person-2',
                    'parameters': {
                        'occupation': 'agent'
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
                    'edited_element_id': 'person-2',
                    'old_element_id': 'occupation'
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
                    'edited_element_id': 'certainty-7',
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

    async def test_modify_unsaved_reference_from_listable_to_unlistable(self):
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
                        'entity_type': 'person',
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        added_properties = EntityProperty.objects.filter(
            entity__xml_id='person-6',
            entity__file_id=file_id
        )
        assert added_properties.count() == 0

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'old_element_id': 'person-6',
                    'new_element_id': 'date-2'
                }
            ]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        added_properties = EntityProperty.objects.filter(
            entity__xml_id='person-6',
            entity__file_id=file_id
        )
        assert added_properties.count() == 0

        await communicator.disconnect()

    async def test_modify_unsaved_reference_from_unlistable_to_listable(self):
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

        date_entities_in_db = Entity.objects.filter(type='date')
        assert date_entities_in_db.count() == 2

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
                            'when': '2000-01-01'
                        }
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert date_entities_in_db.count() == 3

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'old_element_id': 'date-3',
                    'new_element_id': 'ingredient-0'
                }
            ]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert date_entities_in_db.count() == 2

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
                    "edited_element_id": "certainty-7",
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue113:
    """The annotator fails to create annotations for the name attribute"""

    async def test_add_certainty_to_event_name_property(self):
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
                    'new_element_id': 'event-0/name',
                    'parameters': {
                        'categories': ['imprecision'],
                        'locus': 'value',
                        'certainty': 'medium',
                        'asserted_value': 'something',
                        'description': ''
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty_to_new_event_name_property(self):
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
                        'entity_type': 'event',
                    }
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
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'event-1',
                    'parameters': {
                        'name': 'Greater Poland uprising'
                    }
                }
            ]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'event-1/name',
                    'parameters': {
                        'categories': ['imprecision'],
                        'locus': 'value',
                        'certainty': 'medium',
                        'asserted_value': 'something',
                        'description': ''
                    }
                }
            ]
        }
        request_nr = 3

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue114:
    """Attribute uncertainty annotations are not correctly saved/retrieved"""

    async def test_xpath_for_added_entity_property_is_generated_properly(self):
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
                        'entity_type': 'person',
                    }
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
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-6',
                    'parameters': {
                        'age': 'adult'
                    }
                }
            ]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'person-6/age',
                    'parameters': {
                        'categories': ['credibility'],
                        'locus': 'value',
                        'certainty': 'medium',
                        'asserted_value': '21',
                        'description': ''
                    }
                }
            ]
        }
        request_nr = 3

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue122:
    """Creating a second reference to an entity is not reflected in the operations"""

    async def test_adding_reference_in_complex_operation_is_reflected_in_operations(self):
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
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 265,
                        'end_pos': 271,
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 0,
                    'new_element_id': 'event-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue124:
    """Editing annotations causes original annotation duplicate"""

    async def test_modifying_certainty_creates_new_unsaved_certainty_with_changes(self):
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
                    'element_type': 'certainty',
                    'method': 'PUT',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'categories',
                    'parameters': {
                        'categories': ['credibility', 'imprecision']
                    }
                },
                {
                    'element_type': 'certainty',
                    'method': 'PUT',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'certainty',
                    'parameters': {
                        'certainty': 'low'
                    }
                },
                {
                    'element_type': 'certainty',
                    'method': 'PUT',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'asserted_value',
                    'parameters': {
                        'asserted_value': 'sugar cane'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssueUnnamed01:
    """Entities properties doesn't exists after file download"""

    async def test_added_entities_are_properly_rendered_in_downloaded_file(self):
        """Case replicated without issue description"""

        test_name = inspect.currentframe().f_code.co_name

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        project = Project.objects.get(id=project_id)
        directory = Directory.objects.get(project=project, name=project.title, parent_dir=None)
        source_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'music_xml_clean.xml')

        upload_file(client, source_file_path, directory.id)

        file_id = 4
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        response = await communicator.receive_json_from()
        request_nr = 0
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 317,
                        'end_pos': 331,
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 0,
                    'parameters': {
                        'entity_type': 'person',
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-0',
                    'parameters': {
                        'forename': 'Freddy'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-0',
                    'parameters': {
                        'surname': 'Mercury'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-0',
                    'parameters': {
                        'sex': 'M'
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1, 2, 3, 4, 5]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

        expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'expected_files',
                                          'music_xml_clean_expected.xml')
        expected_xml = read_file(expected_file_path)

        file = File.objects.order_by('-id')[0]
        latest_file_version = file.file_versions.latest('id')
        result_xml = download_file(client, file_id, latest_file_version.number)

        assert result_xml == expected_xml


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue137:
    """Discarding entity creation causes error"""

    async def test_discarding_adding_reference_does_not_cause_an_error(self):
        test_name = inspect.currentframe().f_code.co_name

        user_id = 2
        project_id = 2

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        project = Project.objects.get(id=project_id)
        project_files = project.file_set
        assert project_files.count() == 0

        directory = Directory.objects.get(project=project, name=project.title, parent_dir=None)
        source_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'music.xml')
        upload_file(client, source_file_path, directory.id)
        assert project_files.count() == 1

        file_id = project_files.latest('id').id
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
                        'start_pos': 341,
                        'end_pos': 355,
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 0,
                    'parameters': {
                        'entity_type': 'person',
                    }
                },
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [2]
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
