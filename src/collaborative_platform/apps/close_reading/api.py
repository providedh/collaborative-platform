import json

from django.http import HttpRequest, HttpResponse

from apps.files_management.models import File
from apps.files_management.helpers import upload_file
from apps.files_management.helpers import uploaded_file_object_from_string
from apps.projects.models import Project

from .annotation_history_handler import AnnotationHistoryHandler, NoVersionException
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
                'data': None,
            }

            response = json.dumps(response)

            return HttpResponse(response, status=304, content_type='application/json')

        file_version_old = File.objects.get(id=file_id).version_number

        xml_content = annotating_xml_content.xml_content
        file_name = annotating_xml_content.file_name
        uploaded_file = uploaded_file_object_from_string(xml_content, file_name)

        project = Project.objects.get(id=project_id)
        upload_response = upload_file(uploaded_file, project, request.user)

        file_version_new = upload_response.version_number

        if file_version_old == file_version_new:
            response = {
                'status': 304,
                'message': 'There is no changes to save in file with id: {0}.'.format(file_id),
                'data': None,
            }

            response = json.dumps(response)

            return HttpResponse(response, status=304, content_type='application/json')
        else:
            response = {
                'status': 200,
                'message': 'File with id: {0} was saved.'.format(file_id),
                'data': None
            }

            response = json.dumps(response)

            return HttpResponse(response, status=200, content_type='application/json')


# TODO secure this with permisision checkiing decorator
# @login_required()
def history(request, project_id, file_id, file_version):  # type: (HttpRequest, int, int, int) -> HttpResponse
    if request.method == 'GET':
        try:
            annotation_history_handler = AnnotationHistoryHandler(project_id, file_id)
            history = annotation_history_handler.get_history(file_version)
        except NoVersionException as exception:
            response = {
                'status': 400,
                'message': str(exception),
                'data': None,
            }

            response = json.dumps(response)

            return HttpResponse(response, status=400, content_type='application/json')

        response = {
            'status': 200,
            'message': 'OK',
            'data': history,
        }

        response = json.dumps(response)

        return HttpResponse(response, status=200, content_type='application/json')
