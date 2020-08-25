from dal import autocomplete

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator

from apps.core.models import Profile
from apps.files_management.models import Directory
from apps.views_decorators import objects_exists, user_has_access
from apps.loggers import ProjectsLogger

from .forms import ContributorForm, ProjectEditForm
from .models import Project, Contributor


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
@user_has_access()
def project_files(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(id=project_id)

    context = {
        'title': project.title,
        'alerts': None,
        'project': project,
    }

    return render(request, 'projects/project_files.html', context)


@login_required
@objects_exists
@user_has_access('AD')
def settings(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(pk=project_id)
    ContributorFormset = inlineformset_factory(Project,
                                               Contributor,
                                               fields=('profile', 'permissions'),
                                               widgets={'profile': autocomplete.ModelSelect2(url='projects:user_autocomplete')},
                                               labels={'profile': 'User'},
                                               extra=1)

    contributor_formset = ContributorFormset(instance=project)
    project_edit_form = ProjectEditForm(instance=project)

    # without this form autocomplete widget is not visible in formset
    dummy_form = ContributorForm

    alerts = []

    if request.method == 'POST' and 'title' in request.POST:
        project_edit_form = ProjectEditForm(request.POST, instance=project)

        if project_edit_form.is_valid():
            project_edit_form.save()

            directory = Directory.objects.get(project=project, parent_dir=None, deleted=False)

            if directory.name != project_edit_form.cleaned_data['title']:
                directory.rename(project.title, request.user)

            alert = {
                'type': 'success',
                'message': "Project properties changed successfully"
            }
            alerts.append(alert)
        else:
            alert = {
                'type': 'warning',
                'message': "Form invalid"
            }
            alerts.append(alert)

    if request.method == 'POST' and 'contributors-TOTAL_FORMS' in request.POST:
        contributor_formset = ContributorFormset(request.POST, instance=project)

        if contributor_formset.is_valid():
            cleaned_forms = [form.cleaned_data for form in contributor_formset.forms]

            valid_forms = []

            for form in cleaned_forms:
                if 'profile' in form:
                    valid_forms.append(form)

            sorted_forms = sorted(valid_forms, key=lambda k: k['DELETE'])

            for form in sorted_forms:
                try:
                    contributor = Contributor.objects.get(profile=form['profile'], project_id=project_id)
                except Contributor.DoesNotExist:
                    user = form['profile'].user

                    contributor = Contributor(profile=form['profile'], project_id=project_id, permissions='RO', user=user)

                contributor_id = contributor.user.id
                old_permissions = contributor.permissions
                new_permissions = form['permissions']

                if form['DELETE']:
                    if old_permissions == 'AD':
                        admins = Contributor.objects.filter(project_id=project_id, permissions='AD')

                        if len(admins) > 1 and contributor.id is not None:
                            contributor.delete()

                            ProjectsLogger().log_removing_user_from_project(project_id, request.user.id, contributor_id)

                        else:
                            alert = {
                                'type': 'warning',
                                'message': "Can't remove contributor: {0}. There must be at least one administrator "
                                           "in a project.".format(str(contributor.profile)),
                            }

                            alerts.append(alert)
                    elif contributor.id is not None:
                        contributor.delete()

                        ProjectsLogger().log_removing_user_from_project(project_id, request.user.id, contributor_id)

                elif old_permissions != new_permissions:
                    if old_permissions == 'AD':
                        admins = Contributor.objects.filter(project_id=project_id, permissions='AD')

                        if not len(admins) > 1:
                            alert = {
                                'type': 'warning',
                                'message': "Can't change permissions for contributor: {0}. There must be at least one "
                                           "administrator in a project.".format(str(contributor.profile)),
                            }
                            alerts.append(alert)
                        else:
                            contributor.permissions = new_permissions
                            contributor.save()

                            ProjectsLogger().log_changing_user_permissions(project_id, request.user.id, contributor_id,
                                                                           old_permissions, new_permissions)

                    else:
                        contributor.permissions = new_permissions
                        contributor.save()

                        ProjectsLogger().log_changing_user_permissions(project_id, request.user.id, contributor_id,
                                                                       old_permissions, new_permissions)

                elif contributor.id is None:
                    contributor.save()

                    ProjectsLogger().log_adding_user_to_project(project_id, contributor.user.id, new_permissions,
                                                                request.user.id)

            contributor_formset = ContributorFormset(instance=project)

    context = {
        'title': 'Contributors',
        'project': project,
        'alerts': alerts,
        'contributor_formset': contributor_formset,
        'project_edit_form': project_edit_form,
        'dummy_form': dummy_form,
    }

    return render(request, 'projects/settings.html', context)


@method_decorator(login_required, name='dispatch')
class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Profile.objects.all()
        qs = qs.exclude(user__username='admin')

        if self.q:
            qs = qs.filter(Q(user__username__istartswith=self.q) |
                           Q(user__first_name__istartswith=self.q) |
                           Q(user__last_name__istartswith=self.q))

        return qs


@login_required
@objects_exists
@user_has_access('AD')
def delete(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(id=project_id)

    project_title = project.title

    project.delete()

    alert = {
        'type': 'success',
        'message': "Project: {0} removed successfully.".format(project_title),
    }

    context = {
        'title': 'Projects',
        'alerts': [alert],
    }

    return render(request, 'projects/projects.html', context)
