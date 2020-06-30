import inspect
import json
import os
import pytest

from channels.testing import WebsocketCommunicator

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Entity, EntityProperty
from apps.files_management.models import FileVersion

from collaborative_platform.routing import application


SCRIPT_DIR = os.path.dirname(__file__)


# TODO: Extract creating communicators and disconnecting them to pytest fixture
# TODO: Figure out how to reset database after each test inside class and reduce number of test classes


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
                        'start_pos': 405,
                        'end_pos': 409,
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb2:
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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
class TestAnnotatorWithWsAndDb3:
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
        assert len(date_entities_in_db) == 3

        await communicator.disconnect()


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb4:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb5:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb6:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb7:
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb8:
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb9:
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
                        'entity_properties': {
                            'when': '1410-07-15'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb10:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb11:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb12:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb13:
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
                        'entity_properties': {
                            'name': 'new date'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb14:
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
                    'edited_element_id': 'place-0',
                    'old_element_id': 'geo'
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
class TestAnnotatorWithWsAndDb15:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb16:
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
                    'edited_element_id': 'person-0',
                    'old_element_id': 'name',
                    'parameters': {
                        'name': 'Bruce'
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
class TestAnnotatorWithWsAndDb17:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb18:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb19:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb20:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb21:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb22:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb23:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb24:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb25:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb26:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb27:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb28:
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb29:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb30:
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
                        'end_pos': 342,
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb31:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb32:
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb33:
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
                        'entity_properties': {
                            'when': '2000-01-01'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb34:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb35:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb36:
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb37:
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
                        'entity_properties': {
                            'when': '1410-07-15'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb38:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb39:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb40:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb41:
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb42:
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
            'method': 'discard',
            'payload': [1]
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
class TestAnnotatorWithWsAndDb43:
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
                        'entity_properties': {
                            'name': 'new date'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb44:
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
                    'edited_element_id': 'person-0',
                    'old_element_id': 'name',
                    'parameters': {
                        'name': 'Bruce'
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb45:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb46:
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
                    'edited_element_id': 'place-0',
                    'old_element_id': 'geo'
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb47:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb48:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb49:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb50:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb51:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb52:
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
                        'end_pos': 342,
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb53:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb54:
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb55:
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
                        'entity_properties': {
                            'when': '2000-01-01'
                        }
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb56:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb57:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb58:
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
                        'entity_properties': {
                            'forename': 'Bugs',
                            'surname': 'Bunny',
                            'sex': 'M'
                        }
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb59:
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
                        'entity_properties': {
                            'when': '1410-07-15'
                        }
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb60:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb61:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb62:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb63:
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
            entity_version=date_entity_in_db.entityversion_set.all().order_by('-id')[0]
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb64:
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
            'method': 'save',
            'payload': [1]
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
class TestAnnotatorWithWsAndDb65:
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
                        'entity_properties': {
                            'name': 'new date'
                        }
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
            'payload': [3]
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
class TestAnnotatorWithWsAndDb66:
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
                    'edited_element_id': 'person-0',
                    'old_element_id': 'name',
                    'parameters': {
                        'name': 'Bruce'
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb67:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb68:
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
                    'edited_element_id': 'place-0',
                    'old_element_id': 'geo'
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb69:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb70:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb71:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb72:
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


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb73:
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
        )

        assert len(file_versions) == 3

        expected_file_name = f'{test_name}.xml'
        expected_file_path = os.path.join(SCRIPT_DIR, 'result_files', expected_file_name)

        expected_xml = read_file(expected_file_path)
        result_xml = file_versions[0].get_raw_content()

        assert result_xml == expected_xml


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


def verify_response(test_name, response, request_nr):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)
    expected = test_results[test_name][request_nr]

    for field in expected.keys():
        assert response[field] == expected[field]


def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text
