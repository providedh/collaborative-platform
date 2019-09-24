from apps.views_decorators import objects_exists, user_has_access
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from apps.projects.models import Contributor, Project
from apps.files_management.models import File, FileVersion


@login_required
def projects(request):  # type: (HttpRequest) -> JsonResponse
    if request.method == 'GET':
        user = request.user

        contributors = Contributor.objects.filter(user=user)

        response = []

        for contributor in contributors:
            project = {
                'id': contributor.project.id,
                'name': contributor.project.title,
                'permissions': contributor.permissions,
            }

            response.append(project)

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def project_history(request, project_id):  # type: (HttpRequest, int) -> JsonResponse
    if request.method == 'GET':
        response = {
            'info': 'Not implemented. Need to agree an appearance of response.'
        }

        return JsonResponse(response, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def project_files(request, project_id):  # type: (HttpRequest, int) -> JsonResponse
    if request.method == 'GET':
        search = request.GET.get('search', None)
        person = request.GET.get('person', None)

        if search:
            response = {
                'info': 'Not implemented.'
            }

            return JsonResponse(response, status=HttpResponse.status_code)

        elif person:
            response = {
                'info': 'Not implemented.'
            }

            return JsonResponse(response, status=HttpResponse.status_code)

        else:
            files = File.objects.filter(project=project_id).order_by('id')

            response = []

            for file in files:
                file_details = {
                    'id': file.id,
                    'name': file.name,
                    'path': file.get_relative_path(),
                }

                response.append(file_details)

            return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def file(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.filter(id=file_id).get()
        response = file.download()

        return response


def file_body(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        response = {
            'info': 'Not implemented. Need to agree how handle <div> sections in body for plain text.'
        }

        return JsonResponse(response, status=HttpResponse.status_code)
