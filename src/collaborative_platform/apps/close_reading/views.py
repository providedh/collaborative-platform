from django.contrib import auth
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.files_management.models import File
from apps.projects.models import Project, Contributor


@login_required()
def close_reading(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse

    alerts = []

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        alert = {
            'type': 'warning',
            'message': "Project with id: {} doesn't exist.".format(project_id)
        }

        alerts.append(alert)

        context = {
            'title': 'Home',
            'alerts': alerts,
        }

        return render(request, 'core/index.html', context)

    contributor = Contributor.objects.filter(project_id=project_id, user_id=request.user.pk)
    if not contributor:
        alert = {
            'type': 'warning',
            'message': "You aren't contributor in project with id: {}.".format(project_id)
        }

        alerts.append(alert)

        context = {
            'title': 'Home',
            'alerts': alerts,
        }

        return render(request, 'core/index.html', context)

    file = File.objects.get(project_id=project_id, id=file_id)

    context = {
        'title': file.name,
        'alerts': None,
        'file': file,
        'project_id': project_id,
        'file_id': file_id,
    }

    return render(request, 'close_reading/close_reading.html', context)
