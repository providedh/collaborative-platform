import json
import pytest

from django.contrib.auth.models import User
from django.test import Client

from apps.api_vis.models import Clique


@pytest.mark.usefixtures('api_vis_with_db_setup')
@pytest.mark.django_db()
@pytest.mark.integration_tests
class TestApiVisWithDb:
    def test_clique_creation__given_name__given_entities_ids(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        cliques = Clique.objects.all()
        assert cliques.count() == 0

        url = f'/api/vis/projects/{project_id}/cliques/'

        payload = {
            'name': 'first_clique',
            'entities': [11, 15],
            'certainty': 'high',
            'project_version': 6.0,
        }

        response = client.post(url, payload, content_type="application/json")

        assert response.status_code == 200

        cliques = Clique.objects.all()
        assert cliques.count() == 1

        clique = cliques[0]
        assert clique.unifications.count() == 2

        response_content = json.loads(response.content)

        expected_response = {
            'name': 'first_clique',
            'id': 1,
            'unification_statuses': [
                {
                    'id': 11,
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
