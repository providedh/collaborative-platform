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

        user_id = 2
        project_id = 1
        file_id = 1

        communicator = get_communicator_for_logged_in_user(user_id, project_id, file_id)

        connected, _ = await communicator.connect()

        assert connected is True

        await communicator.disconnect()


def get_communicator_for_logged_in_user(user_id, project_id, file_id):
    client = Client()
    user = User.objects.get(id=user_id)
    client.force_login(user=user)

    # Authenticate user by send cookie in the websocket's header doesn't work
    # communicator = WebsocketCommunicator(
    #     application=application,
    #     path=f'/ws/close_reading/{project_id}_{file_id}/',
    #     headers=[(b'cookie', f'sessionid={client.cookies["sessionid"].value}'.encode('ascii'))]
    # )

    # Authenticate user by set user directly to the WebsocketCommunicator's scope
    communicator = WebsocketCommunicator(
        application=application,
        path=f'/ws/close_reading/{project_id}_{file_id}/',
    )

    communicator.scope['user'] = user

    return communicator
