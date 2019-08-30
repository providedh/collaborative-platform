import json
from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse, Http404
from django.shortcuts import render

from apps.files_management.models import File, FileVersion, Directory
from apps.projects.models import Contributor, Project


def objects_exists(view):  # type: (Callable) -> Callable
    """Requirements:
        - decorated view must take 'project_id', 'directory_id', 'file_id' or 'version' argument
    """

    def decorator(*args, **kwargs):
        wanted_kwargs = {
            'project_id': {
                'model': Project,
                'name': 'Project',
            },
            'directory_id': {
                'model': Directory,
                'name': 'Directory',
            },
            'file_id': {
                'model': File,
                'name': 'File',
            }
        }

        for kwarg in wanted_kwargs:
            if kwarg in kwargs:
                model = wanted_kwargs[kwarg]['model']
                model_name = wanted_kwargs[kwarg]['name']
                model_id = kwargs[kwarg]

                try:
                    _ = model.objects.get(id=model_id)
                except model.DoesNotExist:
                    request = args[0]
                    status = HttpResponseBadRequest.status_code
                    message = "{0} with id: {1} doesn't exist.".format(model_name, model_id)
                    bootstrap_alert_type = 'danger'

                    response = __get_response(request, status, bootstrap_alert_type, message)

                    return response

        if 'version' in kwargs:
            if 'file_id' not in kwargs:
                request = args[0]
                status = HttpResponseBadRequest.status_code
                message = "Not found required 'project_id' in given arguments."
                bootstrap_alert_type = 'danger'

                response = __get_response(request, status, bootstrap_alert_type, message)

                return response

            else:
                version = kwargs['version']
                file_id = kwargs['file_id']

                try:
                    _ = FileVersion.objects.get(file_id=file_id, number=version)
                except FileVersion.DoesNotExist:
                    request = args[0]
                    status = HttpResponseBadRequest.status_code
                    message = "Version {} for file with id: {} doesn't exist.".format(version, file_id)
                    bootstrap_alert_type = 'danger'

                    response = __get_response(request, status, bootstrap_alert_type, message)

                    return response

        return view(*args, **kwargs)

    return decorator


def user_has_access(permissions_level=None):
    """Requirements:
        - user must be logged in ('@login_required' from django.contrib.auth.decorators)
        - decorated view must take 'project_id', 'file_id' or 'directory_id' argument
        - project, file or directory must exist ('@exists' from apps.decorators)
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            project_id = __get_project_id(request, **kwargs)
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


def __get_project_id(request, **kwargs):
    if 'project_id' in kwargs:
        project_id = kwargs['project_id']
    elif 'file_id' in kwargs:
        file_id = kwargs['file_id']
        file = File.objects.get(id=file_id)
        project_id = file.project_id
    elif 'directory_id' in kwargs:
        directory_id = kwargs['directory_id']
        directory = Directory.objects.get(id=directory_id)
        project_id = directory.project_id
    elif request.method == "POST" and request.POST.get("data", False):
        data = json.loads(request.POST.get("data"))
        project_id_files, project_id_dirs = None, None

        if 'files' in data:
            ids = set()
            for file_id in data['files']:
                file = File.objects.get(id=file_id)
                ids.add(file.project_id)
            if len(ids) > 1:
                raise Exception("Not all of given files ids in the same project.")
            else:
                project_id_files = ids.pop()

        if 'directories' in data:
            ids = set()
            for dir_id in data['directories']:
                dir = Directory.objects.get(id=dir_id)
                ids.add(dir.project_id)
            if len(ids) > 1:
                raise Exception("Not all of given directories ids in the same project.")
            else:
                project_id_dirs = ids.pop()

        if project_id_files is not None and project_id_dirs is not None:
            if project_id_dirs == project_id_files:
                project_id = project_id_files
            else:
                raise KeyError("Files and dirs from different projects")

        elif project_id_files is not None or project_id_dirs is not None:
            project_id = project_id_files or project_id_dirs
        else:
            raise KeyError("Not found required 'project_id', 'file_id' or 'directory_id' in given arguments")

    else:
        raise KeyError("Not found required 'project_id', 'file_id' or 'directory_id' in given arguments")

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
    return request.path.split('/')[1] == 'api'
