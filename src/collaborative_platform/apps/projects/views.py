from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from apps.views_decorators import objects_exists, user_has_access

from .models import Project, Contributor


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


@login_required
@objects_exists
@user_has_access()
def project(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(id=project_id)
    contributors = Contributor.objects.filter(project_id=project_id)

    contributors_ids = contributors.values_list('user_id', flat=True)

    users = User.objects.filter(id__in=contributors_ids)

    try:
        Contributor.objects.get(user=request.user, project=project, permissions='AD')
    except Contributor.DoesNotExist:
        admin = False
    else:
        admin = True

    context = {
        'title': project.title,
        'alerts': None,
        'project': project,
        'contributors': users,
        'admin': admin,
    }

    return render(request, 'projects/project.html', context)
