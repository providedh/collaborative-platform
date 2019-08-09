from json import dumps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseForbidden, JsonResponse

from apps.files_management.models import File, FileVersion
from apps.projects.models import Contributor, Project
from .files_management import upload_file


@login_required()
def upload(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.FILES:
        files_list = request.FILES.getlist("files")
        if not files_list:
            return HttpResponseBadRequest("File not attached properly")
        try:
            project = int(request.POST.get("project"))
            project = Project.objects.filter(id=project).get()
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


@login_required()
def get_file_version(request, file_id, version):
    try:
        file = File.objects.filter(id=file_id).get()
    except File.DoesNotExist:
        return HttpResponseNotFound(dumps({"message": "File with this id does not exist"}))

    if not file.project.public:
        try:
            Contributor.objects.filter(project=file.project, user=request.user).get()
        except Contributor.DoesNotExist:
            return HttpResponseForbidden(dumps({"message": "User has no access to this project"}))

    try:
        fv = file.versions.filter(number=version).get()  # type: FileVersion
    except FileVersion.DoesNotExist:
        return HttpResponseNotFound(dumps({"message": "Invalid version number for this file"}))

    try:
        creator = model_to_dict(fv.created_by, fields=('id', 'first_name', 'last_name'))
    except (AttributeError, User.DoesNotExist):
        creator = fv.created_by_id

    fv.upload.open('r')
    response = {
        "filename": file.name,
        "version_number": fv.number,
        "creator": creator,
        "body": fv.upload.read()
    }
    fv.upload.close()

    return JsonResponse(response)
