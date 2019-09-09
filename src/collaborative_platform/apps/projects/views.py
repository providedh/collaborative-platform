from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory, modelformset_factory

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

    context = {
        'title': project.title,
        'alerts': None,
        'project': project,
        'contributors': users,
    }

    return render(request, 'projects/project.html', context)


def contributors(request, project_id):  # type: (HttpRequest, int) -> HttpResponse

    project = Project.objects.get(pk=project_id)
    ContributorFormset = modelformset_factory(Contributor, fields=('user', 'permissions'))

    if request.method == 'POST':
        formset = ContributorFormset(request.POST, queryset=Contributor.objects.filter(project__id=project.id))  # a może 'project_id' zamiast 'project__id'?

        if formset.is_valid():
            instances = formset.save(commit=False)

            for instance in instances:
                instance.project = project
                instance.save()

            return redirect('contributors', project_id=project.id)

    formset = ContributorFormset(queryset=Contributor.objects.filter(project__id=project.id))  # a może 'project_id' zamiast 'project__id'?

    return render(request, 'projects/contributors.html', {'formset': formset})
