import os
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Clique, Unification
from apps.files_management.tests.integration_tests.test_file_handling_with_hd_and_db import download_file, read_file


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.mark.usefixtures('file_handling_with_hd_and_db__db_setup', 'reset_db_files_directory_after_each_test')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue164:
    """Retrieving files fail after accepting unifications"""

    def test_file_rendered_correctly_after_adding_unification_without_commit(self):
        user_id = 2
        file_id = 1
        clique_id = 1
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.all()
        assert cliques.count() == 6

        unifications = Unification.objects.all()
        assert unifications.count() == 12

        uncommitted_cliques = cliques.filter(created_in_commit__isnull=True)
        assert uncommitted_cliques.count() == 0

        uncommitted_unifications = unifications.filter(created_in_commit__isnull=True)
        assert uncommitted_unifications.count() == 0

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [20],
            'certainty': 'medium',
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.put(url, payload, content_type="application/json")
        assert response.status_code == 200

        assert cliques.count() == 6
        assert unifications.count() == 13
        assert uncommitted_cliques.count() == 0
        assert uncommitted_unifications.count() == 1

        expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'expected_files',
                                          'issue_164__expected.xml')
        expected_xml = read_file(expected_file_path)

        result_xml = download_file(client, file_id)
        assert result_xml == expected_xml

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'seventh_clique',
            'entities': [1, 16, 21],
            'certainty': 'high',
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200

        assert cliques.count() == 7
        assert unifications.count() == 16
        assert uncommitted_cliques.count() == 1
        assert uncommitted_unifications.count() == 4

        result_xml = download_file(client, file_id)
        assert result_xml == expected_xml
