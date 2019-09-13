from dal import autocomplete

from django import forms
from apps.projects.models import Contributor, Project


class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ('user', )
        widgets = {
            'user': autocomplete.ModelSelect2(url='user_autocomplete')
        }


class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'license', 'public')
