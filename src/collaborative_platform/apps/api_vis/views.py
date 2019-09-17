from django.shortcuts import render
from apps.views_decorators import objects_exists, user_has_access
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from apps.projects.models import Contributor, Project


@login_required
def projects(request):  # type: (HttpRequest) -> JsonResponse
    if request.method == 'GET':
        user = request.user

        contributors = Contributor.objects.filter(user=user)
        projects = [contributor.project for contributor in contributors]

        response = []

        for project in projects:
            project_details = {
                'id': project.id,
                'name': project.title,
            }

            response.append(project_details)

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)
