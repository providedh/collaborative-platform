from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .files_management import upload_file


def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("files")
        for file in files_list:
            upload_file(file)
        return HttpResponseRedirect("/")  # TODO: replace this with actual path
    raise
