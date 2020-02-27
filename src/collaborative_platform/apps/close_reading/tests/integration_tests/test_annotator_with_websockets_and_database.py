import pytest

from channels.testing import WebsocketCommunicator

from django.contrib.auth.models import User
from django.test import Client

from collaborative_platform.routing import application


TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@pytest.mark.asyncio
@pytest.mark.django_db
@pytest.mark.integration_tests
class TestAnnotatorWithWebsocketsAndDatabase:
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


def get_communicator(project_id, file_id, user_id=None):
    communicator = WebsocketCommunicator(
        application=application,
        path=f'/ws/close_reading/{project_id}_{file_id}/',
    )

    if user_id:
        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user=user)

        communicator.scope['user'] = user

    return communicator
