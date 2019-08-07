from django.http import HttpRequest, HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from .files_management import upload_file


# TODO secure this with permisision checkiing decorator
def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("files")
        if not files_list:
            return HttpResponseBadRequest("File not attached properly")
        try:
            project = int(request.POST.get("project"))
        except:
            return HttpResponseBadRequest("Invalid project id")
        try:
            parent_dir = int(request.POST.get("parent_dir"))
        except:
            parent_dir = None

        try:
            for file in files_list:
                upload_file(file, project, parent_dir)
        except:
            return HttpResponseServerError("Unknown error while uploading")
        return HttpResponse("OK")
    return HttpResponseBadRequest("Invalid request method or files not attached")


