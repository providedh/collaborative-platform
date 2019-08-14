from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import render

from apps.files_management.models import File
from apps.projects.models import Contributor, Project


def project_exist(view):  # type: (Callable) -> Callable
    """Requirements:
        - decorated function must take 'project_id' argument
    """

    def decorator(*args, **kwargs):
        project_id = kwargs['project_id']

        try:
            _ = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            request = args[0]
            status = HttpResponseBadRequest.status_code
            message = "Project with id: {} doesn't exist.".format(project_id)
            bootstrap_alert_type = 'danger'

            response = __get_response(request, status, bootstrap_alert_type, message)

            return response

        return view(*args, **kwargs)

    return decorator


def file_exist(view):  # type: (Callable) -> Callable
    """Requirements:
        - decorated function must take 'file_id' argument
    """

    def decorator(*args, **kwargs):
        file_id = kwargs['file_id']

        try:
            _ = File.objects.get(id=file_id)
        except File.DoesNotExist:
            request = args[0]
            status = HttpResponseBadRequest.status_code
            message = "File with id: {} doesn't exist.".format(file_id)
            bootstrap_alert_type = 'danger'

            response = __get_response(request, status, bootstrap_alert_type, message)

            return response

        return view(*args, **kwargs)

    return decorator


def has_access(permissions_level=None):
    """Requirements:
        - user must be logged in ('@login_required' from django.contrib.auth.decorators)
        - decorated function must take 'project_id' or 'file_id' argument
        - project or file must exist ('@project_exist' from apps.projects.decorators or '@file_exist' from
          apps.files_management.decorators)
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            project_id = __get_project_id(**kwargs)
            user_id = request.user.id

            contributor = Contributor.objects.filter(project_id=project_id, user_id=user_id)
            project = Project.objects.get(id=project_id)

            if permissions_level is None:
                if project.public or contributor:
                    return func(request, *args, **kwargs)
            else:
                if contributor:
                    permissions = {
                        'RO': 0,
                        'RW': 1,
                        'AD': 2,
                    }

                    required_permissions = permissions[permissions_level]
                    contributor_permissions = permissions[contributor[0].permissions]

                    if contributor_permissions >= required_permissions:
                        return func(request, *args, **kwargs)

            status = HttpResponseForbidden.status_code
            message = "You dont have enough permissions to perform this action.".format(project_id)
            bootstrap_alert_type = 'warning'

            response = __get_response(request, status, bootstrap_alert_type, message)

            return response
        return inner
    return decorator


def __get_project_id(**kwargs):
    if 'project_id' in kwargs:
        project_id = kwargs['project_id']
    elif 'file_id' in kwargs:
        file_id = kwargs['file_id']
        file = File.objects.get(id=file_id)
        project_id = file.project_id
    else:
        raise KeyError("Not found required 'project_id' or 'file_id' in given arguments")

    return project_id


def __get_response(request, status, bootstrap_alert_type, message, data=None):
    # type: (HttpRequest, int, str, str, dict) -> HttpResponse
    if __from_api(request):
        response = {
            'status': status,
            'message': message,
            'data': data,
        }

        return JsonResponse(response, status=status)

    else:
        alert = {
            'type': bootstrap_alert_type,
            'message': message
        }

        context = {
            'title': 'Home',
            'alerts': [alert],
        }

        return render(request, 'core/index.html', context)


def __from_api(request):  # type: (HttpRequest) -> bool
    return request.path.split('/')[0] == 'api'
