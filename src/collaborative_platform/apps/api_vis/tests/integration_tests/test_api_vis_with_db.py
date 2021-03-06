import inspect
import json
import os
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Clique, Commit, Unification
from apps.files_management.tests.integration_tests.test_file_handling_with_hd_and_db import download_file
from apps.projects.models import Project


SCRIPT_DIR = os.path.dirname(__file__)


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
        assert cliques.count() == 6

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'seventh_clique',
            'entities': [12, 19],
            'certainty': 'high',
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all().order_by('-id')
        assert cliques.count() == 7

        clique = cliques[0]
        assert clique.unifications.count() == 2

        for unification in clique.unifications.all():
            assert unification.categories.count() == 2

            categories = unification.categories.order_by('id')
            assert categories[0].name == 'ignorance'
            assert categories[1].name == 'incompleteness'

        response_content = json.loads(response.content)

        expected_response = {
            'name': 'seventh_clique',
            'id': 7,
            'unification_statuses': [
                {
                    'id': 12,
                    'status': 200,
                    'message': 'OK',
                },
                {
                    'id': 19,
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
        assert cliques.count() == 6

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
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all().order_by('-id')
        assert cliques.count() == 7

        clique = cliques[0]
        assert clique.unifications.count() == 2

        for unification in clique.unifications.all():
            assert unification.categories.count() == 2

            categories = unification.categories.order_by('id')
            assert categories[0].name == 'ignorance'
            assert categories[1].name == 'incompleteness'

        response_content = json.loads(response.content)

        expected_response = {
            'name': 'Ingwer',
            'id': 7,
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
            'entities': [21],
            'certainty': 'medium',
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.put(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all()
        assert cliques.count() == 6

        clique = cliques[0]
        assert clique.unifications.count() == 3

        last_unification = clique.unifications.latest('id')
        assert last_unification.categories.count() == 2

        categories = last_unification.categories.order_by('id')
        assert categories[0].name == 'ignorance'
        assert categories[1].name == 'incompleteness'

        response_content = json.loads(response.content)

        expected_response = {
            'unification_statuses': [
                {
                    'id': 21,
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
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.put(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all()
        assert cliques.count() == 6

        clique = cliques[0]
        assert clique.unifications.count() == 3

        last_unification = clique.unifications.latest('id')
        assert last_unification.categories.count() == 2

        categories = last_unification.categories.order_by('id')
        assert categories[0].name == 'ignorance'
        assert categories[1].name == 'incompleteness'

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
        assert cliques.count() == 6

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'seventh_clique',
            'entities': [12, 19],
            'certainty': 'high',
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        client.post(url, payload, content_type="application/json")

        cliques = Clique.objects.all()
        assert cliques.count() == 7

        commits = Commit.objects.all()
        assert commits.count() == 5

        project = Project.objects.get(
            id=project_id
        )

        last_project_version = project.versions.order_by('-id')[0]
        assert last_project_version.file_version_counter == 8
        assert last_project_version.commit_counter == 5

        cliques_committed = Clique.objects.filter(
            created_in_commit__isnull=False
        )

        assert cliques_committed.count() == 6

        unifications_committed = Unification.objects.filter(
            created_in_commit__isnull=False
        )

        assert unifications_committed.count() == 12

        url = f'/api/vis/projects/{project_id}/commits/'

        payload = {
            'message': 'First commit message'
        }

        response = client.post(url, payload, content_type="application/json")
        assert response.status_code == 200

        commits = Commit.objects.all()
        assert commits.count() == 6

        project = Project.objects.get(
            id=project_id
        )

        last_project_version = project.versions.order_by('-id')[0]
        assert last_project_version.file_version_counter == 8
        assert last_project_version.commit_counter == 6

        cliques = Clique.objects.all()
        assert cliques.count() == 7

        cliques_committed = Clique.objects.filter(
            created_in_commit__isnull=False
        )

        assert cliques_committed.count() == 7

        unifications_committed = Unification.objects.filter(
            created_in_commit__isnull=False
        )

        assert unifications_committed.count() == 14

    def test_delete_clique(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.filter(
            deleted_by__isnull=True
        )

        assert cliques.count() == 5

        unifications = Unification.objects.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 9

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'cliques': [1, 99],
            'project_version': 6.5,
        }

        response = client.delete(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.filter(
            deleted_by__isnull=True
        )

        assert cliques.count() == 4

        unifications = Unification.objects.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 8

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

        assert unifications.count() == 1

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [11, 15],
            'project_version': 6.3,
        }

        response = client.delete(url, payload, content_type="application/json")

        assert response.status_code == 200

        clique.refresh_from_db()
        unifications = clique.unifications.filter(
            deleted_by__isnull=True
        )

        assert unifications.count() == 0

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

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('types', {'types': 'person'}),
        ('users', {'users': '2'}),
        ('start_date', {'start_date': '2020-06-28T12:05:30+01:00'}),
        ('end_date', {'end_date': '2020-06-28T12:13:00+01:00'}),
        ('date', {'date': '2020-06-28T12:15:00+01:00'}),
        ('project_version', {'project_version': '6.3'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_all_cliques_in_project(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        url = f'/api/vis/projects/{project_id}/cliques/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('types', {'types': 'person'}),
        ('users', {'users': '2'}),
        ('date', {'date': '2020-06-30T10:28:00+01:00'}),
        ('project_version', {'project_version': '6.5'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_all_entities_in_project(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        url = f'/api/vis/projects/{project_id}/entities/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('types', {'types': 'person'}),
        ('users', {'users': '2'}),
        ('start_date', {'start_date': '2020-06-28T12:10:00+01:00'}),
        ('end_date', {'end_date': '2020-06-28T12:13:00+01:00'}),
        ('date', {'date': '2020-06-28T12:15:00+01:00'}),
        ('project_version', {'project_version': '6.3'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_unbound_entities_in_project(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        url = f'/api/vis/projects/{project_id}/entities/unbound_entities/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('types', {'types': 'ingredient'}),
        ('users', {'users': '2'}),
        ('start_date', {'start_date': '2020-06-28T12:05:30+01:00'}),
        ('end_date', {'end_date': '2020-06-28T12:13:00+01:00'}),
        ('date', {'date': '2020-06-28T12:15:00+01:00'}),
        ('project_version', {'project_version': '6.3'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_all_cliques_which_include_entities_from_given_file(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        file_id = 1

        url = f'/api/vis/projects/{project_id}/files/{file_id}/cliques/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('types', {'types': 'person'}),
        ('users', {'users': '2'}),
        ('date', {'date': '2020-06-30T10:28:00+01:00'}),
        ('project_version', {'project_version': '6.5'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_all_entities_from_given_file(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        file_id = 1

        url = f'/api/vis/projects/{project_id}/files/{file_id}/entities/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('users', {'users': '2'}),
        ('date', {'date': '2020-06-30T10:28:00+01:00'}),
        ('project_version', {'project_version': '6.5'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_all_certainties_from_given_file(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        file_id = 1

        url = f'/api/vis/projects/{project_id}/files/{file_id}/certainties/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    test_parameters_names = "filtering_case, qs_parameters"
    test_parameters_list = [
        ('no_filtering', None),
        ('types', {'types': 'person'}),
        ('users', {'users': '2'}),
        ('start_date', {'start_date': '2020-06-28T12:10:00+01:00'}),
        ('end_date', {'end_date': '2020-06-28T12:13:00+01:00'}),
        ('date', {'date': '2020-06-28T12:15:00+01:00'}),
        ('project_version', {'project_version': '6.3'})
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_get_unbound_entities_in_file(self, filtering_case, qs_parameters):
        test_name = inspect.currentframe().f_code.co_name
        test_name = f'{test_name}_{filtering_case}'

        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        file_id = 1

        url = f'/api/vis/projects/{project_id}/files/{file_id}/entities/unbound_entities/'

        if qs_parameters:
            url = add_qs_parameters(url, qs_parameters)

        response = client.get(url)

        assert response.status_code == 200

        response_content = json.loads(response.content)
        verify_response(test_name, response_content)

    def test_get_uncommitted_changes(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        url = f'/api/vis/projects/{project_id}/commits/uncommitted_changes/'

        response = client.get(url)
        assert response.status_code == 200

        response_content = json.loads(response.content)

        expected_response = {
            'uncommitted_changes': {
                'cliques_to_create': [],
                'cliques_to_delete': [],
                'unifications_to_add': [],
                'unifications_to_remove': []
            },
        }

        assert response_content == expected_response

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'seventh_clique',
            'entities': [12, 19],
            'certainty': 'high',
            'categories': ['ignorance', 'incompleteness'],
            'project_version': 6.5,
        }

        response = client.post(url, payload, content_type="application/json")
        assert response.status_code == 200

        clique_id = 1

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [21],
            'certainty': 'medium',
            'project_version': 8.5,
        }

        response = client.put(url, payload, content_type="application/json")
        assert response.status_code == 200

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'cliques': [2],
            'project_version': 8.5,
        }

        response = client.delete(url, payload, content_type="application/json")
        assert response.status_code == 200

        url = f'/api/vis/projects/{project_id}/cliques/{clique_id}/entities/'

        payload = {
            'entities': [11],
            'certainty': 'high',
            'project_version': 8.5,
        }

        response = client.delete(url, payload, content_type="application/json")
        assert response.status_code == 200

        url = f'/api/vis/projects/{project_id}/commits/uncommitted_changes/'

        response = client.get(url)
        assert response.status_code == 200

        response_content = json.loads(response.content)

        expected_response = {
            'uncommitted_changes': {
                'cliques_to_create': [
                    {
                        'id': 7,
                        'name': 'seventh_clique',
                        'created_by_id': 2,
                        'type': 'ingredient'
                     }
                ],
                'cliques_to_delete': [
                    {
                        'id': 2,
                        'name': 'second_clique',
                        'created_by_id': 2,
                        'type': 'ingredient'
                    }
                ],
                'unifications_to_add': [
                    {
                        'id': 13,
                        'clique_id': 7,
                        'clique_name': 'seventh_clique',
                        'entity_id': 12,
                        'entity_name': 'Ingwer',
                        'certainty': 'high',
                        'categories': ['ignorance', 'incompleteness'],
                        'created_by': 2,
                        'entity_file_name': 'group_0_long_annotated_0_modified_xml',
                        'entity_type': 'ingredient',
                        'entity_xml_id': 'ingredient-1',
                    },
                    {
                        'id': 14,
                        'clique_id': 7,
                        'clique_name': 'seventh_clique',
                        'entity_id': 19,
                        'entity_name': 'Sand',
                        'certainty': 'high',
                        'categories': ['ignorance', 'incompleteness'],
                        'created_by': 2,
                        'entity_file_name': 'group_0_long_annotated_1_modified_xml',
                        'entity_type': 'ingredient',
                        'entity_xml_id': 'ingredient-1',
                    },
                    {
                        'id': 15,
                        'clique_id': 1,
                        'clique_name': 'first_clique',
                        'entity_id': 21,
                        'entity_name': 'Sand',
                        'certainty': 'medium',
                        'categories': [],
                        'created_by': 2,
                        'entity_file_name': 'group_0_long_annotated_2_modified_xml',
                        'entity_type': 'ingredient',
                        'entity_xml_id': 'ingredient-1',
                    },
                ],
                'unifications_to_remove': [
                    {
                        'id': 1,
                        'clique_id': 1,
                        'clique_name': 'first_clique',
                        'entity_id': 11,
                        'entity_name': 'Rag',
                        'certainty': 'high',
                        'categories': [],
                        'created_by': 2,
                        'entity_file_name': 'group_0_long_annotated_0_modified_xml',
                        'entity_type': 'ingredient',
                        'entity_xml_id': 'ingredient-0',
                    },
                    {
                        'id': 3,
                        'clique_id': 2,
                        'clique_name': 'second_clique',
                        'entity_id': 18,
                        'entity_name': 'Jus',
                        'certainty': 'high',
                        'categories': ['credibility'],
                        'created_by': 2,
                        'entity_file_name': 'group_0_long_annotated_1_modified_xml',
                        'entity_type': 'ingredient',
                        'entity_xml_id': 'ingredient-0',
                    },
                    {
                        'id': 4,
                        'clique_id': 2,
                        'clique_name': 'second_clique',
                        'entity_id': 20,
                        'entity_name': 'Ingwer',
                        'certainty': 'high',
                        'categories': ['credibility'],
                        'created_by': 2,
                        'entity_file_name': 'group_0_long_annotated_2_modified_xml',
                        'entity_type': 'ingredient',
                        'entity_xml_id': 'ingredient-0',
                    },
                ]
            },
        }

        assert response_content == expected_response

    def test_certainties_generated_from_unifications_are_properly_appended(self):
        user_id = 2
        file_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        expected_file_path = os.path.join(SCRIPT_DIR, 'test_files', 'expected_files',
                                          'certainties_generated_from_unifications_are_properly_appended__expected.xml')
        expected_xml = read_file(expected_file_path)
        result_xml = download_file(client, file_id)

        assert result_xml == expected_xml


def add_qs_parameters(url, qs_parameters):
    url += '?'

    for parameter, value in qs_parameters.items():
        if '+' in value:
            value = value.replace('+', '%2B')

        url += f'{parameter}={value}'

    return url


def verify_response(test_name, response):
    test_results_file_path = os.path.join(SCRIPT_DIR, 'tests_results.json')
    test_results = read_file(test_results_file_path)
    test_results = json.loads(test_results)
    expected = test_results[test_name]

    assert response == expected


def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text
