import inspect
import json
import os
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.projects.models import Project
from apps.files_management.models import Directory
from apps.files_management.tests.integration_tests.test_file_handling_with_hd_and_db import upload_file
from apps.close_reading.tests.integration_tests.test_annotator_with_ws_and_db import get_communicator


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.mark.usefixtures('api_vis_with_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue158:
    """Annotating entities makes the entity API to stop working for that file"""

    async def test_api_endpoint_returns_correct_response_after_annotating_entity(self):
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
        source_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'group_0_long_clean_0.xml')
        upload_file(client, source_file_path, directory.id)
        assert project_files.count() == 1

        file_id = project_files.latest('id').id
        file_entities_url = f'/api/vis/projects/{project_id}/files/{file_id}/entities/'
        response = client.get(file_entities_url)
        assert response.status_code == 200

        response_content = json.loads(response.content)
        request_nr = 0
        verify_response(test_name, response_content, request_nr)

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
                        'start_pos': 253,
                        'end_pos': 260,
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

        response = client.get(file_entities_url)
        assert response.status_code == 200

        response_content = json.loads(response.content)
        request_nr = 3
        verify_response(test_name, response_content, request_nr)


def verify_response(test_name, response, request_nr):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results_for_issues.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)
    expected = test_results[test_name][request_nr]

    if type(expected) == list:
        for i, item in enumerate(expected):
            assert response[i] == expected[i]

    elif type(expected) == dict:
        for field in expected.keys():
            assert response[field] == expected[field]


def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text
