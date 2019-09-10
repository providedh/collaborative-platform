from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory

from apps.views_decorators import objects_exists, user_has_access

from .models import Project, Contributor
from dal import autocomplete
from .forms import ContributorForm


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


@login_required
@objects_exists
@user_has_access('AD')
def contributors(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(pk=project_id)
    ContributorFormset = inlineformset_factory(Project, Contributor, fields=('user', 'permissions'), extra=1, widgets={'user': autocomplete.ModelSelect2(url='user_autocomplete')})

    if request.method == 'POST':
        formset = ContributorFormset(request.POST, instance=project)

        if formset.is_valid():
            cleaned_forms = [form.cleaned_data for form in formset.forms]

            alerts = []

            for form in cleaned_forms:
                if 'user' not in form:
                    continue

                try:
                    contributor = Contributor.objects.get(user=form['user'], project_id=project_id)
                except Contributor.DoesNotExist:
                    contributor = Contributor(user=form['user'], project_id=project_id, permissions='RO')

                if form['DELETE'] == True:
                    if contributor.permissions == 'AD':
                        admins = Contributor.objects.filter(project_id=project_id, permissions='AD')

                        if len(admins) > 1 and contributor.id is not None:
                            contributor.delete()
                        else:
                            alert = {
                                'type': 'warning',
                                'message': "Can't remove contributor: {0}. There must be at least one administrator in a project.".format(contributor.user.username),
                            }

                            alerts.append(alert)
                    elif contributor.id is not None:
                        contributor.delete()

                elif contributor.permissions != form['permissions']:
                    contributor.permissions = form['permissions']
                    contributor.save()

            formset = ContributorFormset(instance=project)

            # without this form autocomplete widget is not visible in formset
            form = ContributorForm

            return render(request, 'projects/contributors.html', {'formset': formset, 'form': form, 'alerts': alerts})

    formset = ContributorFormset(instance=project)

    # without this form autocomplete widget is not visible in formset
    form = ContributorForm

    return render(request, 'projects/contributors.html', {'formset': formset, 'form': form})


class UserAutocomplete(autocomplete.Select2QuerySetView):
    # TODO: View decorators not working for class based views. Secure this view manually
    def get_queryset(self):
        qs = User.objects.all()

        if self.q:
            qs = qs.filter(username__istartswith=self.q)

        return qs
