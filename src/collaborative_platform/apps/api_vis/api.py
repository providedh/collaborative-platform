import json

from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotModified, JsonResponse

from apps.api_vis.helpers import validate_keys_and_types
from apps.api_vis.db_handler import DbHandler
from apps.exceptions import BadRequest, NotModified
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access('RW')
def project_cliques(request, project_id):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
                'project_version': float,
            }
            optional_keys = {
                'name': str
            }

            validate_keys_and_types(request_data, required_keys, optional_keys)

            db_handler = DbHandler(project_id, request.user)
            clique_id, clique_name = db_handler.create_clique(request_data)

            entities = request_data['entities']
            project_version_nr = request_data['project_version']
            unification_statuses = []

            for entity in entities:
                unification_status = {}

                if type(entity) is int:
                    unification_status.update({'id': entity})
                elif type(entity) is dict:
                    unification_status.update(entity)

                status_update = db_handler.add_unification(clique_id, entity, project_version_nr)
                unification_status.update(status_update)
                unification_statuses.append(unification_status)

        except (BadRequest, JSONDecodeError) as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {
                'name': clique_name,
                'id': clique_id,
                'unification_statuses': unification_statuses,
            }

            return JsonResponse(response)

@login_required
@objects_exists
@user_has_access('RW')
def clique_entities(request, project_id, clique_id):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
                'project_version': float,
            }
            optional_keys = {
                'name': str
            }

            validate_keys_and_types(request_data, required_keys, optional_keys)

            db_handler = DbHandler(project_id, request.user)

            entities = request_data['entities']
            project_version_nr = request_data['project_version']
            unification_statuses = []

            for entity in entities:
                unification_status = {}

                if type(entity) is int:
                    unification_status.update({'id': entity})
                elif type(entity) is dict:
                    unification_status.update(entity)

                status_update = db_handler.add_unification(clique_id, entity, project_version_nr)
                unification_status.update(status_update)
                unification_statuses.append(unification_status)

        except (BadRequest, JSONDecodeError) as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {
                'unification_statuses': unification_statuses,
            }

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def commits(request, project_id):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)

            optional_keys = {
                'message': str,
            }

            validate_keys_and_types(request_data, optional_name_type_template=optional_keys)

            message = request_data.get('message')

            db_handler = DbHandler(project_id, request.user)
            db_handler.commit_changes(message)

        except NotModified as exception:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        except (BadRequest, JSONDecodeError) as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            status = HttpResponse.status_code

            response = {
                'status': status,
                'message': 'OK'
            }

            return JsonResponse(response)
