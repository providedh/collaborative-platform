import json

from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotModified, JsonResponse

from apps.api_vis.helpers import parse_query_string
from apps.api_vis.db_handler import DbHandler
from apps.api_vis.request_handler import RequestHandler
from apps.api_vis.request_validator import RequestValidator, validate_keys_and_types
from apps.exceptions import BadRequest, NotModified
from apps.views_decorators import objects_exists, user_has_access


BAD_REQUEST_STATUS = HttpResponseBadRequest.status_code
NOT_MODIFIED_STATUS = HttpResponseNotModified.status_code
OK_STATUS = HttpResponse.status_code


@login_required
@objects_exists
@user_has_access('RW')
def project_cliques(request, project_id):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_clique_creation_data(request_data)

            response = RequestHandler().create_clique(project_id, request.user, request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

    elif request.method == "GET":
        try:
            request_data = parse_query_string(request.GET)

            response = RequestHandler().get_project_cliques(project_id, request.user, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_clique_delete_data(request_data)

            response = RequestHandler().delete_clique(project_id, request.user, request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


@login_required
@objects_exists
@user_has_access('RW')
def file_cliques(request, project_id, file_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            response = RequestHandler().get_file_cliques(file_id, request.user, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


@login_required
@objects_exists
@user_has_access('RW')
def project_entities(request, project_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            response = RequestHandler().get_project_entities(project_id, request.user, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


@login_required
@objects_exists
@user_has_access('RW')
def file_entities(request, project_id, file_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            response = RequestHandler().get_file_entities(file_id, request.user, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


@login_required
@objects_exists
@user_has_access('RW')
def project_unbound_entities(request, project_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            response = RequestHandler().get_project_unbound_entities(project_id, request.user, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


@login_required
@objects_exists
@user_has_access('RW')
def file_unbound_entities(request, project_id, file_id):
    if request.method == 'GET':
        try:
            qs_parameters = parse_query_string(request.GET)

            db_handler = DbHandler(project_id, request.user)
            response = db_handler.get_unbound_entities_in_file(qs_parameters, file_id)

        except BadRequest as exception:
            response = {
                'status': BAD_REQUEST_STATUS,
                'message': str(exception),
            }

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

        else:
            return JsonResponse(response, safe=False)


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
            certainty = request_data['certainty']
            unification_statuses = []

            for entity in entities:
                unification_status = {}

                if type(entity) is int:
                    unification_status.update({'id': entity})
                elif type(entity) is dict:
                    unification_status.update(entity)

                status_update = db_handler.add_unification(clique_id, entity, certainty, project_version_nr)
                unification_status.update(status_update)
                unification_statuses.append(unification_status)

        except (BadRequest, JSONDecodeError) as exception:
            response = {
                'status': BAD_REQUEST_STATUS,
                'message': str(exception),
            }

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

        else:
            response = {
                'unification_statuses': unification_statuses,
            }

            return JsonResponse(response)

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'project_version': float,
            }

            validate_keys_and_types(request_data, required_keys)

            db_handler = DbHandler(project_id, request.user)

            entities_ids = request_data['entities']
            project_version_nr = request_data['project_version']
            delete_statuses = []

            for entity_id in entities_ids:
                delete_status = {}

                delete_status.update({'id': entity_id})

                status_update = db_handler.delete_unification(clique_id, entity_id, project_version_nr)
                delete_status.update(status_update)
                delete_statuses.append(delete_status)

        except (BadRequest, JSONDecodeError) as exception:
            response = {
                'status': BAD_REQUEST_STATUS,
                'message': str(exception),
            }

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

        else:
            response = {
                'delete_statuses': delete_statuses,
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

            validate_keys_and_types(request_data, optional_key_type_pairs=optional_keys)

            message = request_data.get('message')

            db_handler = DbHandler(project_id, request.user)
            db_handler.commit_changes(message)

        except NotModified as exception:
            response = {
                'status': NOT_MODIFIED_STATUS,
                'message': str(exception),
            }

            return JsonResponse(response, status=NOT_MODIFIED_STATUS)

        except (BadRequest, JSONDecodeError) as exception:
            response = {
                'status': BAD_REQUEST_STATUS,
                'message': str(exception),
            }

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

        else:
            response = {
                'status': OK_STATUS,
                'message': 'OK'
            }

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def uncommitted_changes(request, project_id):
    if request.method == 'GET':
        try:
            db_handler = DbHandler(project_id, request.user)
            response = db_handler.get_uncommitted_changes()

        except BadRequest as exception:
            response = {
                'status': BAD_REQUEST_STATUS,
                'message': str(exception),
            }

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

        else:
            return JsonResponse(response, safe=False)
