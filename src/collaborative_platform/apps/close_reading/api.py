import json

from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse, HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from io import BytesIO

from apps.files_management.models import File
from apps.files_management.files_management import upload_file
from apps.projects.models import Contributor, Project

from .models import AnnotatingXmlContent


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
                'message': 'There is no file to save with id: {0} for project: {1}.'.format(file_id, project_id),
            }

            response = json.dumps(response)

            return HttpResponse(response, status=304, content_type='application/json')

        file = BytesIO(annotating_xml_content.xml_content.encode('utf-8'))
        file_name = annotating_xml_content.file_name

        file_version_old = File.objects.get(id=file_id).version_number

        uploaded_file = UploadedFile(file=file, name=file_name)
        project = Project.objects.get(id=project_id)
        upload_response = upload_file(uploaded_file, project, request.user)

        file_version_new = upload_response.version_number

        if file_version_old == file_version_new:
            response = {
                'status': 304,
                'message': 'There is no changes to save in file with id: {0}.'.format(file_id),
            }

            response = json.dumps(response)

            return HttpResponse(response, status=304, content_type='application/json')
        else:
            response = {
                'status': 200,
                'message': 'File with id: {0} was saved.'.format(file_id),
            }

            response = json.dumps(response)

            return HttpResponse(response, status=200, content_type='application/json')


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
