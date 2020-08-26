import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.views_decorators import objects_exists, user_has_access

from .annotation_history_handler import AnnotationHistoryHandler


logger = logging.getLogger('close_reading')


@login_required
@objects_exists
@user_has_access()
def history(request, project_id, file_id, version):  # type: (HttpRequest, int, int, int) -> HttpResponse
    if request.method == 'GET':
        annotation_history_handler = AnnotationHistoryHandler(project_id, file_id)
        history = annotation_history_handler.get_history(version)

        status = HttpResponse.status_code

        response = {
            'status': status,
            'message': 'OK',
            'data': history,
        }

        return JsonResponse(response, status=status)


@login_required
def current_user(request): # type: (HttpRequest) -> HttpResponse
    if request.method == 'GET':
        user = request.user

        status = HttpResponse.status_code

        response = {
            'id': 'person' + str(user.id),
            'forename': user.first_name,
            'surname': user.last_name,
            'email': user.email,
        }

        return JsonResponse(response, status=status)
