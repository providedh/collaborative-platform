from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseForbidden, JsonResponse

from apps.files_management.models import File
from apps.projects.models import Contributor
# from .files_management import upload_file
from .models import AnnotatingXmlContent
import json
from io import StringIO, BytesIO

from apps.files_management.files_management import upload_file
from django.core.files.uploadedfile import UploadedFile


# TODO secure this with permisision checkiing decorator
# @login_required()
def save(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == "PUT":
        file_symbol = '{0}_{1}'.format(project_id, file_id)

        try:
            annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=file_symbol)
        except AnnotatingXmlContent.DoesNotExist:
            response = {
                'status': 304,
                'message': 'There is no file to save with id: {0} for project: {1}'.format(file_id, project_id),
            }

            response = json.dumps(response)

            return HttpResponse(response, status=304, content_type='application/json')

        file = BytesIO(annotating_xml_content.xml_content.encode('utf-8'))
        file_name = annotating_xml_content.file_name

        uploaded_file = UploadedFile(file=file, name=file_name)

        upload_response = upload_file(uploaded_file, project_id)

        a = 'asd'











    #     files_list = request.FILES.getlist("files")
    #     if not files_list:
    #         return HttpResponseBadRequest("File not attached properly")
    #     try:
    #         project = int(request.POST.get("project"))
    #     except:
    #         return HttpResponseBadRequest("Invalid project id")
    #     try:
    #         parent_dir = int(request.POST.get("parent_dir"))
    #     except:
    #         parent_dir = None
    #
    #     try:
    #         for file in files_list:
    #             upload_file(file, project, parent_dir)
    #     except:
    #         return HttpResponseServerError("Unknown error while uploading")
    #     return HttpResponse("OK")
    # return HttpResponseBadRequest("Invalid request method or files not attached")


def annotation_history(request, project_id, file_if, file_version):
    pass

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
