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
        files = File.objects.filter(project=project_id)

        response = []

        for file in files:
            file_version = FileVersion.objects.get(file=file, number=file.version_number)

            file_details = {
                'id': file.id,
                'name': file.name,
                'path': file_version.upload.url,
                'version': file.version_number,
            }

            response.append(file_details)

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)
