import os
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Clique, Entity, Unification
from apps.files_management.models import Directory
from apps.files_management.tests.integration_tests.test_file_handling_with_hd_and_db import download_file, read_file, \
    upload_file
from apps.projects.models import Project


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.mark.usefixtures('file_handling_with_hd_and_db__db_setup', 'reset_db_files_directory_after_each_test')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestIssue164:
    """Retrieving files fail after accepting unifications"""

    def test_file_rendered_correctly_after_adding_unification_without_commit(self):
        """Case replicated from first issue description"""

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

    def test_file_rendered_correctly_after_adding_unification_without_commit_with_for_new_project(self):
        """Case replicated from second issue description"""

        user_id = 2

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        projects = Project.objects.all()
        assert projects.count() == 2

        url = f'/api/projects/create/'

        payload = {
            "description": "",
            "entities": [
                {"body_list": False, "color": "#ff7f00", "icon": "\uf007", "name": "person"},
                {"body_list": False, "color": "#cecece", "icon": "\uf274", "name": "event"},
                {"body_list": False, "color": "#b4edfc", "icon": "\uf1ad", "name": "org"},
                {"body_list": False, "color": "#b4d38d", "icon": "\uf466", "name": "object"},
                {"body_list": False, "color": "#204191", "icon": "\uf279", "name": "place"},
                {"body_list": False, "color": "#868788", "icon": "\uf073", "name": "date"},
                {"body_list": False, "color": "#eab9e4", "icon": "\uf017", "name": "time"},
                {"body_list": False, "color": "#aaaaaa", "icon": "\uf042", "name": "song"},
                {"body_list": False, "color": "#aaaaaa", "icon": "\uf042", "name": "band"}
            ],
            "taxonomy": [
                {"color": "#9270a8", "description": "", "name": "ignorance", "xml_id": "ignorance"},
                {"color": "#cc4c3b", "description": "", "name": "credibility", "xml_id": "credibility"},
                {"color": "#f1d155", "description": "", "name": "imprecision", "xml_id": "imprecision"},
                {"color": "#67b2ac", "description": "", "name": "incompleteness", "xml_id": "incompleteness"}
            ],
            "title": "Music history"
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200
        assert projects.count() == 3

        project = projects.latest('id')
        uploaded_files = project.file_set.all()
        assert uploaded_files.count() == 0

        entities_offset = Entity.objects.count()

        directory = Directory.objects.get(project=project, name=project.title, parent_dir=None)
        source_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'music_history.xml')
        upload_file(client, source_file_path, directory.id)
        assert uploaded_files.count() == 1

        source_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'source_files', 'music.xml')
        upload_file(client, source_file_path, directory.id)
        assert uploaded_files.count() == 2

        cliques = project.clique_set.all()
        assert cliques.count() == 0

        unifications = project.unifications.all()
        assert unifications.count() == 0

        uncommitted_cliques = cliques.filter(created_in_commit__isnull=True)
        assert uncommitted_cliques.count() == 0

        uncommitted_unifications = unifications.filter(created_in_commit__isnull=True)
        assert uncommitted_unifications.count() == 0

        url = f'/api/vis/projects/{project.id}/cliques/'

        first_entity_id = 7
        second_entity_id = 30

        first_entity_id += entities_offset
        second_entity_id += entities_offset

        payload = {
            'entities': [first_entity_id, second_entity_id],
            'certainty': 'very high',
            'project_version': 4.0
        }

        response = client.post(url, payload, content_type="application/json")
        assert response.status_code == 200

        assert cliques.count() == 1
        assert unifications.count() == 2
        assert uncommitted_cliques.count() == 1
        assert uncommitted_unifications.count() == 2

        first_file = uploaded_files.order_by('id')[0]
        second_file = uploaded_files.order_by('id')[1]

        expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'expected_files',
                                          'issue_164__music__expected.xml')
        expected_xml = read_file(expected_file_path)

        result_xml = download_file(client, first_file.id)
        assert result_xml == expected_xml

        expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'expected_files',
                                          'issue_164__music_history__expected.xml')
        expected_xml = read_file(expected_file_path)

        result_xml = download_file(client, second_file.id)
        assert result_xml == expected_xml
