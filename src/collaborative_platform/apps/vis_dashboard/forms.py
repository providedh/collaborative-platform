from django import forms

class DashboardCreateForm(forms.Form):
    name = forms.CharField(label='Name', max_length=255)
    description = forms.CharField(label='Description', required=False, widget=forms.Textarea)

class DashboardEditForm(forms.Form):
    name = forms.CharField(label='Name', max_length=255)
    description = forms.CharField(label='Description', required=False, widget=forms.Textarea)