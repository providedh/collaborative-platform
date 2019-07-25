from django.http import HttpRequest, HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render
from .files_management import upload_file


def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("files")
        if not files_list:
            return HttpResponseBadRequest("File not attached properly")
        try:
            for file in files_list:
                upload_file(file)
        except:
            return HttpResponseServerError("Unknown error while uploading")
        return HttpResponse("OK")
    return HttpResponseBadRequest("Invalid request method or files not attached")
