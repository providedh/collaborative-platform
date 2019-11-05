import json
from functools import wraps
from json import JSONDecodeError
from typing import Callable

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse, Http404, \
    RawPostDataException
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
            },
            'user_id': {
                'model': User,
                'name': 'User',
            }
        }

        for kwarg in wanted_kwargs:
            if kwarg in kwargs:
                model = wanted_kwargs[kwarg]['model']
                model_name = wanted_kwargs[kwarg]['name']
                model_id = kwargs[kwarg]

                try:
                    if model_name in ['File', 'Directory']:
                        _ = model.objects.get(id=model_id, deleted=False)
                    else:
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
        - project, file or directory must exist ('@objects_exists' from apps.decorators)
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
    project_id, file_project_id, directory_project_id, post_project_id = None, None, None, None
    print(kwargs)
    if 'project_id' in kwargs:
        project_id = kwargs['project_id']
    if 'file_id' in kwargs:
        file_id = kwargs['file_id']
        file = File.objects.get(id=file_id, deleted=False)
        file_project_id = file.project_id
    if 'directory_id' in kwargs:
        directory_id = kwargs['directory_id']
        directory = Directory.objects.get(id=directory_id, deleted=False)
        directory_project_id = directory.project_id
    try:
        if request.method in ("POST", "PUT") and request.body:
            try:
                data = json.loads(request.body)
            except TypeError:
                raise KeyError("Not found required 'project_id', 'file_id' or 'directory_id' "
                               "in given arguments and POST body is empty")
            except (JSONDecodeError, UnicodeDecodeError):
                pass
            else:
                project_id_files = check_if_all_in_one_project(data, 'files')
                project_id_dirs = check_if_all_in_one_project(data, 'directories')

                if project_id_files is not None and project_id_dirs is not None:
                    if project_id_dirs == project_id_files:
                        post_project_id = project_id_files
                    else:
                        raise KeyError("Files and dirs from different projects")

                elif project_id_files is not None or project_id_dirs is not None:
                    post_project_id = project_id_files or project_id_dirs
    except RawPostDataException:
        pass

    print(f"pro_id={project_id}")
    any_id = project_id or file_project_id or directory_project_id or post_project_id
    if any_id is None:
        raise KeyError("Not found required 'project_id', 'file_id' or 'directory_id' in given arguments")

    if all(map(lambda x: x in (any_id, None), (project_id, file_project_id, directory_project_id, post_project_id))):
        return any_id
    else:
        raise Exception("Not all parameters are parts of the same project or none parameters given!")


def check_if_all_in_one_project(data, key):
    E = {'files': File,
         'directories': Directory}[key]
    project_id = None
    if key in data:
        ids = set()
        for id in data[key]:
            entity = E.objects.get(id=id)
            ids.add(entity.project_id)
        if len(ids) > 1:
            raise Exception("Not all of given {} ids in the same project.".format(key))
        else:
            project_id = ids.pop()
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
