import inspect
import json
import os
import pytest

from apps.close_reading.tests.integration_tests.test_annotator_with_ws_and_db import get_communicator, read_file


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.mark.usefixtures('annotator_with_ws_and_db_setup', 'reset_db_files_directory_before_each_test')
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssues:
    # @pytest.mark.xfail
    # async def test_111_unsaved_uncertainty_annotations_are_not_correctly_deleted(self):
    #     # TODO: consider if better way will be let user edit/delete not saved elements, or disable this possibility for
    #     #  all elements, not only for certainties
    #
    #     test_name = inspect.currentframe().f_code.co_name
    #
    #     project_id = 1
    #     file_id = 1
    #     user_id = 2
    #
    #     communicator = get_communicator(project_id, file_id, user_id)
    #
    #     await communicator.connect()
    #     await communicator.receive_json_from()
    #
    #     request = {
    #         'method': 'modify',
    #         'payload': [
    #             {
    #                 'method': 'POST',
    #                 'element_type': 'certainty',
    #                 'new_element_id': 'ab-0',
    #                 'parameters': {
    #                     'categories': ['ignorance', 'incompleteness'],
    #                     'locus': 'value',
    #                     'certainty': 'low',
    #                     'description': 'Test'
    #                 }
    #             }
    #         ]
    #     }
    #     request_nr = 0
    #
    #     await communicator.send_json_to(request)
    #     response = await communicator.receive_json_from()
    #     verify_response(test_name, response, request_nr)
    #
    #     request = {
    #         'method': 'modify',
    #         'payload': [
    #             {
    #                 'method': 'DELETE',
    #                 'element_type': 'certainty',
    #                 'edited_element_id': 'certainty-5',
    #             }
    #         ]
    #     }
    #     request_nr = 1
    #
    #     await communicator.send_json_to(request)
    #     response = await communicator.receive_json_from()
    #     verify_response(test_name, response, request_nr)
    #
    #     await communicator.disconnect()

    async def test_delete_unsaved_tag(self):
        """Helper for solving issue #111"""

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
                                      "the operation that created it."

        await communicator.disconnect()


def verify_response(test_name, response, request_nr):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results_for_issues.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)
    expected = test_results[test_name][request_nr]

    for field in expected.keys():
        assert response[field] == expected[field]
