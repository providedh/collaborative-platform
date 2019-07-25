from django import forms


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    project = forms.IntegerField()
    parent_dir = forms.CharField()
    file = forms.FileField()
