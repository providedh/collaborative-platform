from dal import autocomplete

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator

from apps.views_decorators import objects_exists, user_has_access
from apps.core.models import Profile

from .forms import ContributorForm
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
@user_has_access('AD')
def settings(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(pk=project_id)
    ContributorFormset = inlineformset_factory(Project,
                                               Contributor,
                                               fields=('profile', 'permissions'),
                                               widgets={'profile': autocomplete.ModelSelect2(url='user_autocomplete')},
                                               labels={'profile': 'User'},
                                               extra=1)

    if request.method == 'POST':
        formset = ContributorFormset(request.POST, instance=project)

        if formset.is_valid():
            cleaned_forms = [form.cleaned_data for form in formset.forms]

            valid_forms = []

            for form in cleaned_forms:
                if 'profile' in form:
                    valid_forms.append(form)

            sorted_forms = sorted(valid_forms, key=lambda k: k['DELETE'])

            alerts = []

            for form in sorted_forms:
                try:
                    contributor = Contributor.objects.get(profile=form['profile'], project_id=project_id)
                except Contributor.DoesNotExist:
                    user = form['profile'].user

                    contributor = Contributor(profile=form['profile'], project_id=project_id, permissions='RO', user=user)

                if form['DELETE']:
                    if contributor.permissions == 'AD':
                        admins = Contributor.objects.filter(project_id=project_id, permissions='AD')

                        if len(admins) > 1 and contributor.id is not None:
                            contributor.delete()
                        else:
                            alert = {
                                'type': 'warning',
                                'message': "Can't remove contributor: {0}. There must be at least one administrator "
                                           "in a project.".format(str(contributor.user)),
                            }

                            alerts.append(alert)
                    elif contributor.id is not None:
                        contributor.delete()

                elif contributor.permissions != form['permissions']:
                    contributor.permissions = form['permissions']
                    contributor.save()

                elif contributor.id is None:
                    contributor.save()

            formset = ContributorFormset(instance=project)

            # without this form autocomplete widget is not visible in formset
            form = ContributorForm

            context = {
                'formset': formset,
                'form': form,
                'project': project,
                'alerts': alerts,
                'title': 'Contributors',
            }

            return render(request, 'projects/settings.html', context)

    formset = ContributorFormset(instance=project)

    # without this form autocomplete widget is not visible in formset
    form = ContributorForm

    context = {
        'formset': formset,
        'form': form,
        'project': project,
        'title': 'Contributors',
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
