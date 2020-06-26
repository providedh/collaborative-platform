import json
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Clique, Commit, Unification
from apps.projects.models import Project


@pytest.mark.usefixtures('api_vis_with_db_setup')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.integration_tests
class TestApiVisWithDb:
    def test_clique_creation__given_name__given_entities_ids(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.all()
        assert cliques.count() == 3

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'fourth_clique',
            'entities': [12, 15],
            'certainty': 'high',
            'project_version': 6.3,
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all().order_by('-id')
        assert cliques.count() == 4

        clique = cliques[0]
        assert clique.unifications.count() == 2

        response_content = json.loads(response.content)

        expected_response = {
            'name': 'fourth_clique',
            'id': 4,
            'unification_statuses': [
                {
                    'id': 12,
                    'status': 200,
                    'message': 'OK',
                },
                {
                    'id': 15,
                    'status': 200,
                    'message': 'OK',
                },
            ]
        }

        assert response_content == expected_response

    def test_clique_creation__name_not_given__given_entities_xml_ids(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.all()
        assert cliques.count() == 3

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'entities': [
                {
                    'file_path': 'Project_1/group_0_long_annotated_0_modified_xml',
                    'xml_id': 'ingredient-1',
                },
                {
                    'file_path': 'Project_1/group_0_long_annotated_1_modified_xml',
                    'xml_id': 'ingredient-1',
                },
            ],
            'certainty': 'high',
            'project_version': 6.3,
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all().order_by('-id')
        assert cliques.count() == 4

        clique = cliques[0]
        assert clique.unifications.count() == 2

        response_content = json.loads(response.content)

        expected_response = {
            'name': 'Ingwer',
            'id': 4,
            'unification_statuses': [
                {
                    'file_path': 'Project_1/group_0_long_annotated_0_modified_xml',
                    'xml_id': 'ingredient-1',
                    'status': 200,
                    'message': 'OK',
                },
                {
                    'file_path': 'Project_1/group_0_long_annotated_1_modified_xml',
                    'xml_id': 'ingredient-1',
                    'status': 200,
                    'message': 'OK',
                },
            ],
        }

        assert response_content == expected_response

    def test_add_entities_to_existing_clique__given_entities_ids(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        clique_id = 1

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [16],
            'certainty': 'medium',
            'project_version': 6.3,
        }

        response = client.put(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all()
        assert cliques.count() == 3

        clique = cliques[0]
        assert clique.unifications.count() == 3

        response_content = json.loads(response.content)

        expected_response = {
            'unification_statuses': [
                {
                    'id': 16,
                    'status': 200,
                    'message': 'OK',
                },
            ]
        }

        assert response_content == expected_response

    def test_add_entities_to_existing_clique__given_entities_xml_ids(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        clique_id = 1

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [
                {
                    'file_path': 'Project_1/group_0_long_annotated_2_modified_xml',
                    'xml_id': 'ingredient-0',
                },
            ],
            'certainty': 'medium',
            'project_version': 6.3,
        }

        response = client.put(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all()
        assert cliques.count() == 3

        clique = cliques[0]
        assert clique.unifications.count() == 3

        response_content = json.loads(response.content)

        expected_response = {
            'unification_statuses': [
                {
                    'file_path': 'Project_1/group_0_long_annotated_2_modified_xml',
                    'xml_id': 'ingredient-0',
                    'status': 200,
                    'message': 'OK',
                },
            ]
        }

        assert response_content == expected_response

    def test_commit_changes(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.all()
        assert cliques.count() == 3

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'fourth_clique',
            'entities': [12, 15],
            'certainty': 'high',
            'project_version': 6.3,
        }

        client.post(url, payload, content_type="application/json")

        commits = Commit.objects.all()
        assert commits.count() == 3

        project = Project.objects.get(
            id=project_id
        )

        last_project_version = project.versions.order_by('-id')[0]
        assert last_project_version.file_version_counter == 6
        assert last_project_version.commit_counter == 3

        cliques = Clique.objects.all()
        assert cliques.count() == 4

        cliques_committed = Clique.objects.filter(
            created_in_commit__isnull=False
        )

        assert cliques_committed.count() == 3

        unifications_committed = Unification.objects.filter(
            created_in_commit__isnull=False
        )

        assert unifications_committed.count() == 6

        url = f'/api/vis/projects/{project_id}/commits/'

        payload = {
            'message': 'First commit message'
        }

        response = client.post(url, payload, content_type="application/json")
        assert response.status_code == 200

        commits = Commit.objects.all()
        assert commits.count() == 4

        project = Project.objects.get(
            id=project_id
        )

        last_project_version = project.versions.order_by('-id')[0]
        assert last_project_version.file_version_counter == 6
        assert last_project_version.commit_counter == 4

        cliques = Clique.objects.all()
        assert cliques.count() == 4

        cliques_committed = Clique.objects.filter(
            created_in_commit__isnull=False
        )

        assert cliques_committed.count() == 4

        unifications_committed = Unification.objects.filter(
            created_in_commit__isnull=False
        )

        assert unifications_committed.count() == 8

    def test_delete_clique(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.filter(
            deleted_by__isnull=True
        )

        assert cliques.count() == 3

        unifications = Unification.objects.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 6

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'cliques': [1, 99],
            'project_version': 6.3,
        }

        response = client.delete(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.filter(
            deleted_by__isnull=True
        )

        assert cliques.count() == 2

        unifications = Unification.objects.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 4

        response_content = json.loads(response.content)

        expected_response = {
            'delete_statuses': [
                {
                    'id': 1,
                    'status': 200,
                    'message': 'OK',
                },
                {
                    'id': 99,
                    'status': 400,
                    'message': "Clique with id: 99 doesn't exist in project with id: 1",
                },
            ]
        }

        assert response_content == expected_response

    def test_remove_entity_from_clique(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        clique_id = 1

        clique = Clique.objects.get(id=clique_id)
        unifications = clique.unifications.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 2

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [11, 15],
            'certainty': 'high',
            'project_version': 6.3,
        }

        response = client.delete(url, payload, content_type="application/json")

        assert response.status_code == 200

        clique.refresh_from_db()
        unifications = clique.unifications.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 1

        response_content = json.loads(response.content)

        expected_response = {
            'delete_statuses': [
                {
                    'id': 11,
                    'status': 200,
                    'message': 'OK',
                },
                {
                    'id': 15,
                    'status': 400,
                    'message': "Clique with id: 1 doesn't contain entity with id: 15",
                },
            ]
        }

        assert response_content == expected_response
