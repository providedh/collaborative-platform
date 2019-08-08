from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseForbidden, JsonResponse

from apps.files_management.models import File
from apps.projects.models import Contributor
from .files_management import upload_file


@login_required()
def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("files")
        if not files_list:
            return HttpResponseBadRequest("File not attached properly")
        try:
            project = int(request.POST.get("project"))
        except:  # TODO check level of contribution to authorize user to upload files
            return HttpResponseBadRequest("Invalid project id")
        try:
            parent_dir = int(request.POST.get("parent_dir"))
        except:
            parent_dir = None

        try:
            for file in files_list:
                upload_file(file, project, request.user, parent_dir)
        except:
            return HttpResponseServerError("Unknown error while uploading")
        return HttpResponse("OK")
    return HttpResponseBadRequest("Invalid request method or files not attached")


@login_required()
def get_file_versions(request, file_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    try:
        file = File.objects.filter(id=file_id).get()
    except File.DoesNotExist:
        return HttpResponseNotFound()

    if not file.project.public:
        try:
            Contributor.objects.filter(project_id=file.project.id, user_id=request.user.id).get()
        except Contributor.DoesNotExist:
            return HttpResponseForbidden("User does not have access to this file")

    return JsonResponse(list(file.versions.all().values()), safe=False)
