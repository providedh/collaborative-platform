from dal import autocomplete

from django import forms
from apps.projects.models import Contributor


class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ('user', )
        widgets = {
            'user': autocomplete.ModelSelect2(url='user_autocomplete')
        }
