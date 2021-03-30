import json

from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.api_vis.helpers import parse_query_string
from apps.api_vis.request_handler import RequestHandler
from apps.api_vis.request_validator import RequestValidator
from apps.exceptions import BadRequest, NotModified
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access('RW')
def project_cliques(request, project_id):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_clique_creation_data(request_data)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.create_clique(request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)

    elif request.method == "GET":
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_project_cliques(request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_clique_delete_data(request_data)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.delete_cliques(request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def file_cliques(request, project_id, file_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_file_cliques(request_data, file_id)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def project_entities(request, project_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_project_entities(request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def file_entities(request, project_id, file_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_file_entities(request_data, file_id)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def file_certainties(request, project_id, file_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_file_certainties(request_data, file_id)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def project_certainties(request, project_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_file_certainties(request_data, file_id=None)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def clique_entities(request, project_id, clique_id):
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_put_clique_entities_data(request_data)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.add_entities_to_clique(clique_id, request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_delete_clique_entities_data(request_data)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.remove_entities_from_clique(clique_id, request_data)

            return JsonResponse(response)

        except (BadRequest, JSONDecodeError) as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def project_unbound_entities(request, project_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_project_unbound_entities(request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def file_unbound_entities(request, project_id, file_id):
    if request.method == 'GET':
        try:
            request_data = parse_query_string(request.GET)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_file_unbound_entities(file_id, request_data)

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def commits(request, project_id):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)

            RequestValidator().validate_commit_data(request_data)

            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.create_commit(request_data)

            from apps.nn_disambiguator.helpers import queue_task
            queue_task(project_id, type="L")

            return JsonResponse(response)

        except NotModified as exception:
            response = get_error(exception, NotModified.status_code)

            return JsonResponse(response, status=NotModified.status_code)

        except (BadRequest, JSONDecodeError) as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


@login_required
@objects_exists
@user_has_access('RW')
def uncommitted_changes(request, project_id):
    if request.method == 'GET':
        try:
            request_handler = RequestHandler(project_id, request.user)
            response = request_handler.get_uncommitted_changes()

            return JsonResponse(response, safe=False)

        except BadRequest as exception:
            response = get_error(exception, BadRequest.status_code)

            return JsonResponse(response, status=BadRequest.status_code)


def get_error(exception, status):
    response = {
        'status': status,
        'message': str(exception),
    }

    return response
