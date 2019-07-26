from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from .models import Project, Contributor
from django.contrib.auth.models import User


@login_required()
def projects(request, user_id):  # type: (HttpRequest, int) -> HttpResponse
    if user_id == request.user.pk:
        context = {
            'title': 'Projects',
            'alerts': None,
        }

        return render(request, 'projects/projects.html', context)

    else:
        alerts = [
            {
                'type': 'warning',
                'message': "You can't see another user projects."
            }
        ]

        context = {
            'title': 'Home',
            'alerts': alerts,
        }

        return render(request, 'core/index.html', context)


@login_required()
def project(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
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

    contributors = Contributor.objects.filter(project_id=project_id)

    contributors_ids = []

    for contributor in contributors:
        contributors_ids.append(contributor.user_id)

    users = User.objects.filter(id__in=contributors_ids)

    context = {
        'title': project.title,
        'alerts': None,
        'project': project,
        'contributors': users,
    }

    return render(request, 'projects/project.html', context)
