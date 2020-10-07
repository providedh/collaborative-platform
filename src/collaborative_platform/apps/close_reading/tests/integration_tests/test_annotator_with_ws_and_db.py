import inspect
import json
import os
import pytest

from channels.testing import WebsocketCommunicator

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Entity, EntityProperty
from apps.files_management.models import FileVersion, ProjectVersion

from collaborative_platform.routing import application


SCRIPT_DIR = os.path.dirname(__file__)


# TODO: Extract creating communicators and disconnecting them to pytest fixture


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb:
    async def test_authorized_user_can_connect(self):
        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        connected, _ = await communicator.connect()
        assert connected is True

        response = await communicator.receive_json_from()
        assert response['status'] == 200
        assert response['message'] == 'OK'

        await communicator.send_to(text_data='ping')
        response = await communicator.receive_from()
        assert response == 'pong'

        await communicator.disconnect()

    test_parameters_names = "project_id, file_id, user_id, response_status, response_message"
    test_parameters_list = [
        (999, 1, 2, 400, "Project with id: 999 doesn't exist."),
        (1, 1, None, 403, "You aren't contributor in project with id: 1."),
        (1, 999, 2, 400, "File with id: 999 doesn't exist."),
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    async def test_connecting_exceptions(self, project_id, file_id, user_id, response_status, response_message):
        communicator = get_communicator(project_id, file_id, user_id)

        connected, _ = await communicator.connect()
        assert connected is True

        response = await communicator.receive_json_from()
        assert response['status'] == response_status
        assert response['message'] == response_message

        await communicator.send_to(text_data='ping')
        with pytest.raises(AssertionError):
            _ = await communicator.receive_from()

    async def test_user_get_correct_response_after_connection(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        request_nr = 0

        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_tags_to_text(self):
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
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 425,
                        'end_pos': 429,
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_move_tag_to_new_position(self):
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
                        'method': 'PUT',
                        'element_type': 'tag',
                        'edited_element_id': 'name-3',
                        'parameters': {
                            'start_pos': 272,
                            'end_pos': 362,
                        }
                    }
                ]
            }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_delete_tag_from_text(self):
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
                    'method': 'DELETE',
                    'element_type': 'tag',
                    'edited_element_id': 'name-3'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_reference_to_entity_to_text__entity_doesnt_exist__entity_listable(self):
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

        await communicator.disconnect()

    async def test_add_reference_to_entity_to_text__entity_doesnt_exist__entity_unlistable(self):
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
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        await communicator.disconnect()

    async def test_add_reference_to_entity_to_text__entity_exist__entity_listable(self):
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

        await communicator.disconnect()

    async def test_add_reference_to_entity_to_text__entity_exist__entity_unlistable(self):
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
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'new_element_id': 'date-0'
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_remove_reference_to_entity_from_text__entity_listable(self):
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
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_remove_reference_to_entity_from_text__entity_unlistable(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-2'
        )

        assert date_entity_in_db.deleted_by is None

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            assert entity_property.deleted_by is None

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'date-2',
                    'old_element_id': 'date-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db.refresh_from_db()
        assert date_entity_in_db.deleted_by.id == user_id

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by.id == user_id

        await communicator.disconnect()

    async def test_modify_reference_to_entity__entity_doesnt_exist__entity_listable(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-2'
        )

        assert date_entity_in_db.deleted_by is None

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            assert entity_property.deleted_by is None

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'date-2',
                    'old_element_id': 'date-2',
                    'parameters': {
                        'entity_type': 'person',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db.refresh_from_db()
        assert date_entity_in_db.deleted_by.id == user_id

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by.id == user_id

        await communicator.disconnect()

    async def test_modify_reference_to_entity__entity_doesnt_exist__entity_unlistable(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        await communicator.disconnect()

    async def test_modify_reference_to_entity__entity_exist__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                    'new_element_id': 'ingredient-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_modify_reference_to_entity__entity_exist__entity_unlistable(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'date-1',
                    'old_element_id': 'date-0',
                    'new_element_id': 'date-2'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_add_property_to_entity__entity_listable(self):
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

        await communicator.disconnect()

    async def test_add_property_to_entity__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

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
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_remove_property_from_entity__entity_listable(self):
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
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_remove_property_from_entity__entity_unlistable(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        entity_property = EntityProperty.objects.filter(
            entity_version__entity__xml_id='date-0',
            name='when'
        ).order_by('-id')[0]

        assert entity_property.deleted_by is None

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-0',
                    'old_element_id': 'when'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property.refresh_from_db()
        assert entity_property.deleted_by.id == user_id

        await communicator.disconnect()

    async def test_modify_entity_property__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename',
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

        await communicator.disconnect()

    async def test_modify_entity_property__entity_unlistable(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        entity_property_old = EntityProperty.objects.filter(
            entity_version__entity__xml_id='date-0',
            name='when'
        ).order_by('-id')[0]

        assert entity_property_old.deleted_by is None

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-0',
                    'old_element_id': 'when',
                    'parameters': {
                        'when': '0001-01-01'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property_old.refresh_from_db()
        assert entity_property_old.deleted_by.id == user_id

        entity_property_new = EntityProperty.objects.filter(
            entity__xml_id='date-0',
            entity_version__isnull=True,
            name='when'
        ).order_by('-id')[0]

        assert entity_property_new.created_in_file_version is None

        await communicator.disconnect()

    async def test_add_certainty__to_text(self):
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
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty__to_reference(self):
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
                    'new_element_id': 'name-3@ref',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty__to_entity_type__default_entity(self):
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
                    'new_element_id': 'place-0',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty__to_entity_type__custom_entity(self):
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
                    'new_element_id': 'ingredient-0',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty__to_entity_property(self):
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
                    'new_element_id': 'place-0/country',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty__to_certainty(self):
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
                    'new_element_id': 'certainty-0',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_remove_certainty(self):
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
                    'method': 'DELETE',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_modify_certainty_parameter__modify_categories(self):
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
                    'method': 'PUT',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'categories',
                    'parameters': {
                        'categories': ['imprecision', 'credibility']
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_modify_certainty_parameter__modify_locus(self):
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
                    'method': 'PUT',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'locus',
                    'parameters': {
                        'locus': 'name'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_modify_certainty_parameter__modify_reference(self):
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
                    'method': 'PUT',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'reference',
                    'parameters': {
                        'new_element_id': 'person-2/birth',
                        'locus': 'name'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_complex_operation(self):
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
                    'parameters': {
                        'entity_type': 'person',
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': '0@ref',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 1,
                    'parameters': {
                        'categories': ['credibility'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 3,
                    'parameters': {
                        'categories': ['ignorance'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_adding_tag_to_text(self):
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
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_moving_tag_to_new_position(self):
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
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'name-3',
                    'parameters': {
                        'start_pos': 272,
                        'end_pos': 362,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_deleting_tag_from_text(self):
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
                    'method': 'DELETE',
                    'element_type': 'tag',
                    'edited_element_id': 'name-3'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_adding_reference_to_entity_to_text__entity_doesnt_exist__entity_listable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

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

    async def test_discard_adding_reference_to_entity_to_text__entity_doesnt_exist__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        request = {
            'method': 'discard',
            'payload': [2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_discard_adding_reference_to_entity_to_text__entity_exist__entity_listable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

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

    async def test_discard_adding_reference_to_entity_to_text__entity_exist__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'new_element_id': 'date-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'discard',
            'payload': [2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_discard_modifying_reference_to_entity__entity_doesnt_exist__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'date-2',
                    'old_element_id': 'date-2',
                    'parameters': {
                        'entity_type': 'person',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-2'
        )

        assert date_entity_in_db.deleted_by.id == user_id

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by.id == user_id

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db.refresh_from_db()
        assert date_entity_in_db.deleted_by is None

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by is None

        await communicator.disconnect()

    async def test_discard_modifying_reference_to_entity__entity_doesnt_exist__entity_unlistable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_discard_modifying_reference_to_entity__entity_exist__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                    'new_element_id': 'ingredient-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_modifying_reference_to_entity__entity_exist__entity_unlistable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'date-1',
                    'old_element_id': 'date-0',
                    'new_element_id': 'date-2'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_discard_removing_reference_to_entity_from_text__entity_listable(self):
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
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_removing_reference_to_entity_from_text__entity_unlistable(self):
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
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'date-2',
                    'old_element_id': 'date-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-2'
        )

        assert date_entity_in_db.deleted_by.id == user_id

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            assert entity_property.deleted_by.id == user_id

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db.refresh_from_db()
        assert date_entity_in_db.deleted_by is None

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by is None

        await communicator.disconnect()

    async def test_discard_adding_property_to_entity__entity_listable(self):
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
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_adding_property_to_entity__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

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
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [3]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_modifying_entity_property__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename',
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
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_modifying_entity_property__entity_unlistable(self):
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
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-0',
                    'old_element_id': 'when',
                    'parameters': {
                        'when': '0001-01-01'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property_old = EntityProperty.objects.filter(
            entity_version__entity__xml_id='date-0',
            name='when'
        ).order_by('-id')[0]

        assert entity_property_old.deleted_by.id == user_id

        entity_property_new = EntityProperty.objects.filter(
            entity__xml_id='date-0',
            entity_version__isnull=True,
            name='when'
        ).order_by('-id')[0]

        assert entity_property_new.created_in_file_version is None

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property_old.refresh_from_db()
        assert entity_property_old.deleted_by is None

        entity_property_new = EntityProperty.objects.filter(
            entity__xml_id='date-0',
            entity_version__isnull=True,
            name='when'
        ).order_by('-id')

        assert len(entity_property_new) == 0

        await communicator.disconnect()

    async def test_discard_removing_property_from_entity__entity_listable(self):
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
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_removing_property_from_entity__entity_unlistable(self):
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
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-0',
                    'old_element_id': 'when'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property = EntityProperty.objects.filter(
            entity_version__entity__xml_id='date-0',
            name='when'
        ).order_by('-id')[0]

        assert entity_property.deleted_by.id == user_id

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property.refresh_from_db()
        assert entity_property.deleted_by is None

        await communicator.disconnect()

    async def test_discard_adding_certainty__to_text(self):
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
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_modifying_certainty_parameter__modify_categories(self):
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
                    'method': 'PUT',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'categories',
                    'parameters': {
                        'categories': ['imprecision', 'credibility']
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_removing_certainty(self):
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
                    'method': 'DELETE',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_adding_tag_to_text(self):
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
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_moving_tag_to_new_position(self):
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
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'name-3',
                    'parameters': {
                        'start_pos': 272,
                        'end_pos': 362,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_deleting_tag_from_text(self):
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
                    'method': 'DELETE',
                    'element_type': 'tag',
                    'edited_element_id': 'name-3'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_adding_reference_to_entity_to_text__entity_doesnt_exist__entity_listable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

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
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1, 2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_adding_reference_to_entity_to_text__entity_doesnt_exist__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        request = {
            'method': 'save',
            'payload': [1, 2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        await communicator.disconnect()

    async def test_accept_adding_reference_to_entity_to_text__entity_exist__entity_listable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

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
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1, 2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_adding_reference_to_entity_to_text__entity_exist__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        _ = await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'new_element_id': 'date-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'save',
            'payload': [1, 2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_accept_modifying_reference_to_entity__entity_doesnt_exist__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'date-2',
                    'old_element_id': 'date-2',
                    'parameters': {
                        'entity_type': 'person',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-2'
        )

        assert date_entity_in_db.deleted_by.id == user_id
        assert date_entity_in_db.deleted_in_file_version is None

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by.id == user_id
            assert entity_property.deleted_in_file_version is None

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db.refresh_from_db()
        assert date_entity_in_db.deleted_in_file_version.number == 3

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_in_file_version.number == 3

        await communicator.disconnect()

    async def test_accept_modifying_reference_to_entity__entity_doesnt_exist__entity_unlistable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-3'
        )

        assert date_entity_in_db.created_by.id == user_id
        assert date_entity_in_db.created_in_file_version is None

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            assert entity_property.created_by.id == user_id
            assert entity_property.reated_in_file_version is None

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 3

        date_entity_in_db.refresh_from_db()

        assert date_entity_in_db.created_by.id == user_id
        assert date_entity_in_db.created_in_file_version.number == 3

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.created_by.id == user_id
            assert entity_property.created_in_file_version.number == 3

        await communicator.disconnect()

    async def test_accept_modifying_reference_to_entity__entity_exist__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                    'new_element_id': 'ingredient-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_modifying_reference_to_entity__entity_exist__entity_unlistable(self):
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
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'date-1',
                    'old_element_id': 'date-0',
                    'new_element_id': 'date-2'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entities_in_db = Entity.objects.filter(type='date')
        assert len(date_entities_in_db) == 2

        await communicator.disconnect()

    async def test_accept_removing_reference_to_entity_from_text__entity_listable(self):
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
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'name-4',
                    'old_element_id': 'ingredient-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_removing_reference_to_entity_from_text__entity_unlistable(self):
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
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'date-2',
                    'old_element_id': 'date-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db = Entity.objects.get(
            file_id=file_id,
            xml_id='date-2'
        )

        assert date_entity_in_db.deleted_by.id == user_id
        assert date_entity_in_db.deleted_in_file_version is None

        date_entity_properties_in_db = EntityProperty.objects.filter(
            entity_version=date_entity_in_db.versions.latest('id')
        )

        for entity_property in date_entity_properties_in_db:
            assert entity_property.deleted_by.id == user_id
            assert entity_property.deleted_in_file_version is None

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        date_entity_in_db.refresh_from_db()
        assert date_entity_in_db.deleted_by.id == user_id
        assert date_entity_in_db.deleted_in_file_version.number == 3

        for entity_property in date_entity_properties_in_db:
            entity_property.refresh_from_db()
            assert entity_property.deleted_by.id == user_id
            assert entity_property.deleted_in_file_version.number == 3

        await communicator.disconnect()

    async def test_accept_adding_property_to_entity__entity_listable(self):
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
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_adding_property_to_entity__entity_unlistable(self):
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

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'date',
                    }
                }
            ]
        }

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

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
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1, 2, 3]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_modifying_entity_property__entity_listable(self):
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
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename',
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
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_modifying_entity_property__entity_unlistable(self):
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
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-0',
                    'old_element_id': 'when',
                    'parameters': {
                        'when': '0001-01-01'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property_old = EntityProperty.objects.filter(
            entity_version__entity__xml_id='date-0',
            name='when'
        ).order_by('-id')[0]

        assert entity_property_old.deleted_by.id == user_id

        entity_property_new = EntityProperty.objects.filter(
            entity__xml_id='date-0',
            entity_version__isnull=True,
            name='when'
        ).order_by('-id')[0]

        assert entity_property_new.created_in_file_version is None

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property_old.refresh_from_db()
        assert entity_property_old.deleted_by.id == user_id
        assert entity_property_old.deleted_in_file_version.number == 3

        entity_property_new.refresh_from_db()
        assert entity_property_new.created_in_file_version.number == 3

        await communicator.disconnect()

    async def test_accept_removing_property_from_entity__entity_listable(self):
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
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_removing_property_from_entity__entity_unlistable(self):
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
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'date-0',
                    'old_element_id': 'when'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property = EntityProperty.objects.filter(
            entity_version__entity__xml_id='date-0',
            name='when'
        ).order_by('-id')[0]

        assert entity_property.deleted_by.id == user_id

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        entity_property.refresh_from_db()
        assert entity_property.deleted_by.id == user_id
        assert entity_property.deleted_in_file_version.number == 3

        await communicator.disconnect()

    async def test_accept_adding_certainty__to_text(self):
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
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_modifying_certainty_parameter__modify_categories(self):
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
                    'method': 'PUT',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1',
                    'old_element_id': 'categories',
                    'parameters': {
                        'categories': ['imprecision', 'credibility']
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_accept_removing_certainty(self):
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
                    'method': 'DELETE',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-1'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_saving_file(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        file_versions = FileVersion.objects.filter(
            file_id=file_id,
        )

        assert len(file_versions) == 2

        project_version = ProjectVersion.objects.filter(project_id=project_id).latest('id')
        file_versions_ids = project_version.file_versions.order_by('id').values_list('id', flat=True)
        file_versions_ids = list(file_versions_ids)
        assert file_versions_ids == [2, 4, 6]

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

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

        request = {
            'method': 'save',
            'payload': [1]
        }

        await communicator.send_json_to(request)
        await communicator.receive_json_from()

        await communicator.disconnect()

        file_versions = FileVersion.objects.filter(
            file_id=file_id,
        ).order_by('-id')

        assert len(file_versions) == 3

        project_version = ProjectVersion.objects.latest('id')
        file_versions_ids = project_version.file_versions.order_by('id').values_list('id', flat=True)
        file_versions_ids = list(file_versions_ids)
        assert file_versions_ids == [4, 6, 7]

        expected_file_name = f'{test_name}.xml'
        expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'expected_files', expected_file_name)

        expected_xml = read_file(expected_file_path)
        result_xml = file_versions[0].get_rendered_content()

        assert result_xml == expected_xml

    async def test_adding_dependencies_to_operations(self):
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
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 425,
                        'end_pos': 429,
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
                    'element_type': 'reference',
                    'edited_element_id': 'ab-1',
                    'parameters': {
                        'entity_type': 'person',
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
                    'element_type': 'reference',
                    'edited_element_id': 'ab-2',
                    'new_element_id': 'person-6'
                }
            ]
        }
        request_nr = 3

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
        request_nr = 4

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'ab-2',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 5

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'ab-2@ref',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 6

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'person-6',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 7

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
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 8

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 'certainty-7',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 9

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_removing_dependencies_from_operations_after_dependency_is_saved(self):
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
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 425,
                        'end_pos': 429,
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
                    'element_type': 'reference',
                    'edited_element_id': 1,
                    'new_element_id': 2
                },
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 2,
                    'parameters': {
                        'age': 'adult'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 1,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': '1@ref',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 2,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 4,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 5,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [2]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discarding_operations_when_dependency_is_discarded(self):
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
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 425,
                        'end_pos': 429,
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
                    'element_type': 'reference',
                    'edited_element_id': 1,
                    'new_element_id': 2
                },
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 2,
                    'parameters': {
                        'age': 'adult'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 1,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': '1@ref',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 2,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 4,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 5,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
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

    async def test_forbid_accepting_operation_when_dependencies_are_not_saved(self):
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
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 425,
                        'end_pos': 429,
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
                    'element_type': 'reference',
                    'edited_element_id': 1,
                    'new_element_id': 2
                },
                {
                    'method': 'POST',
                    'element_type': 'entity_property',
                    'edited_element_id': 2,
                    'parameters': {
                        'age': 'adult'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 1,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': '1@ref',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 2,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'name',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 4,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                },
                {
                    'method': 'POST',
                    'element_type': 'certainty',
                    'new_element_id': 5,
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [4]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [2, 3, 4]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'save',
            'payload': [1, 2, 3, 4]
        }
        request_nr = 3

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_tag_to_text_with_tag_inside(self):
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
                        'end_pos': 338,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_certainty_to_divided_tag(self):
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
                        'end_pos': 338,
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
                    'element_type': 'certainty',
                    'new_element_id': 'ab-1',
                    'parameters': {
                        'categories': ['ignorance', 'incompleteness'],
                        'locus': 'value',
                        'certainty': 'low',
                        'description': 'Test'
                    }
                }
            ]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_split_tag_during_tag_move(self):
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
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'ab-0',
                    'parameters': {
                        'start_pos': 528,
                        'end_pos': 548,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_add_reference_to_divided_tag(self):
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
                        'end_pos': 338,
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

        await communicator.disconnect()

    async def test_accept_adding_reference_to_divided_tag(self):
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
                        'end_pos': 338,
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
            'method': 'save',
            'payload': [1, 2]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_discard_moving_tag_with_tag_dividing(self):
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
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'ab-0',
                    'parameters': {
                        'start_pos': 528,
                        'end_pos': 548,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'discard',
            'payload': [1]
        }
        request_nr = 1

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_move_tag_with_joining_tag(self):
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
                        'end_pos': 338,
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
            'method': 'save',
            'payload': [1, 2]
        }
        request_nr = 2

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'name-8',
                    'parameters': {
                        'start_pos': 251,
                        'end_pos': 256,
                    }
                }
            ]
        }
        request_nr = 3

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_users_see_changes_made_by_another_users(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        first_user_id = 2
        second_user_id = 3

        first_communicator = get_communicator(project_id, file_id, first_user_id)
        second_communicator = get_communicator(project_id, file_id, second_user_id)

        await first_communicator.connect()
        await first_communicator.receive_json_from()

        await second_communicator.connect()
        await second_communicator.receive_json_from()

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

        await first_communicator.send_json_to(request)
        first_response = await first_communicator.receive_json_from()
        verify_response(test_name, first_response, request_nr, first_user_id)

        second_response = await second_communicator.receive_json_from()
        verify_response(test_name, second_response, request_nr, second_user_id)

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'POST',
                    'element_type': 'tag',
                    'parameters': {
                        'start_pos': 425,
                        'end_pos': 429,
                    }
                }
            ]
        }
        request_nr = 1

        await second_communicator.send_json_to(request)
        first_response = await first_communicator.receive_json_from()
        verify_response(test_name, first_response, request_nr, first_user_id)

        second_response = await second_communicator.receive_json_from()
        verify_response(test_name, second_response, request_nr, second_user_id)

        await first_communicator.disconnect()
        await second_communicator.disconnect()

    async def test_user_cant_edit_another_users_tag(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 3

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'tag',
                    'edited_element_id': 'date-0',
                    'parameters': {
                        'start_pos': 272,
                        'end_pos': 342,
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_user_cant_delete_another_users_tag(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 3

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'tag',
                    'edited_element_id': 'date-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_user_cant_edit_another_users_reference(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        second_user_id = 3

        second_communicator = get_communicator(project_id, file_id, second_user_id)

        await second_communicator.connect()
        await second_communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'reference',
                    'edited_element_id': 'name-3',
                    'old_element_id': 'person-2',
                    'new_element_id': 'ingredient-0'
                }
            ]
        }
        request_nr = 0

        await second_communicator.send_json_to(request)
        second_response = await second_communicator.receive_json_from()
        verify_response(test_name, second_response, request_nr)

        await second_communicator.disconnect()

    async def test_user_cant_delete_another_users_reference(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 3

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'reference',
                    'edited_element_id': 'name-3',
                    'old_element_id': 'person-2',
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_user_cant_edit_another_users_entity_property(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 3

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'PUT',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename',
                    'parameters': {
                        'forename': 'Peter'
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_user_cant_delete_another_users_entity_property(self):
        test_name = inspect.currentframe().f_code.co_name

        project_id = 1
        file_id = 1
        user_id = 3

        communicator = get_communicator(project_id, file_id, user_id)

        await communicator.connect()
        await communicator.receive_json_from()

        request = {
            'method': 'modify',
            'payload': [
                {
                    'method': 'DELETE',
                    'element_type': 'entity_property',
                    'edited_element_id': 'person-2',
                    'old_element_id': 'forename'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_user_cant_add_property_to_another_users_entity(self):
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

        await communicator.disconnect()

    async def test_user_cant_edit_another_users_certainty(self):
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
                    'method': 'PUT',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-0',
                    'old_element_id': 'categories',
                    'parameters': {
                        'categories': ['new_awesome_category']
                    }
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()

    async def test_user_cant_delete_another_users_certainty(self):
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
                    'method': 'DELETE',
                    'element_type': 'certainty',
                    'edited_element_id': 'certainty-0'
                }
            ]
        }
        request_nr = 0

        await communicator.send_json_to(request)
        response = await communicator.receive_json_from()
        verify_response(test_name, response, request_nr)

        await communicator.disconnect()


def get_communicator(project_id, file_id, user_id=None):
    communicator = WebsocketCommunicator(
        application=application,
        path=f'/ws/close_reading/{project_id}_{file_id}/',
    )

    if user_id:
        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        communicator.scope['user'] = user

    return communicator


def verify_response(test_name, response, request_nr, user_id=None):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)

    if user_id:
        user_id = str(user_id)
        expected = test_results[test_name][request_nr][user_id]
    else:
        expected = test_results[test_name][request_nr]

    for field in expected.keys():
        assert response[field] == expected[field]


def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text
