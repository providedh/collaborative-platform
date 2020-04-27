import inspect
import json
import os
import pytest

from channels.testing import WebsocketCommunicator

from django.contrib.auth.models import User
from django.test import Client

from collaborative_platform.routing import application


SCRIPT_DIR = os.path.dirname(__file__)
TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@pytest.mark.asyncio
@pytest.mark.django_db
@pytest.mark.integration_tests
class TestAnnotatorWithWsAndDb:
    async def test_authorized_user_can_connect(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

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
    async def test_connecting_exceptions(self, project_id, file_id, user_id, response_status, response_message,
                                         settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        communicator = get_communicator(project_id, file_id, user_id)

        connected, _ = await communicator.connect()
        assert connected is True

        response = await communicator.receive_json_from()
        assert response['status'] == response_status
        assert response['message'] == response_message

        await communicator.send_to(text_data='ping')
        with pytest.raises(AssertionError):
            _ = await communicator.receive_from()

    async def test_user_get_correct_response_after_connection(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        connected, _ = await communicator.connect()
        assert connected is True

        response = await communicator.receive_json_from()
        test_name = inspect.currentframe().f_code.co_name

        verify_response(test_name, response)

        await communicator.disconnect()

    async def test_add_tag_to_text(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        project_id = 1
        file_id = 1
        user_id = 2

        communicator = get_communicator(project_id, file_id, user_id)

        connected, _ = await communicator.connect()
        assert connected is True

        request = [{'aaa': 'lalala'}]
        request = json.dumps(request)

        await communicator.send_to(text_data=request)

        response = await communicator.receive_json_from()
        test_name = inspect.currentframe().f_code.co_name

        verify_response(test_name, response)

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


def verify_response(test_name, response):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)
    expected = test_results[test_name]

    for field in expected.keys():
        assert response[field] == expected[field]


def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text
