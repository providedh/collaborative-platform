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
            request_data = parse_query_string(request.GET)

            response = RequestHandler().get_file_unbound_entities(file_id, request.user, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


@login_required
@objects_exists
@user_has_access('RW')
def clique_entities(request, project_id, clique_id):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_put_clique_entities_data(request_data)

            response = RequestHandler().put_clique_entities(clique_id, request.user, request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_delete_clique_entities_data(request_data)

            response = RequestHandler().delete_clique_entities(clique_id, request.user, request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = RequestHandler().get_error(exception, BAD_REQUEST_STATUS)

            return JsonResponse(response, status=BAD_REQUEST_STATUS)


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
