from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseNotModified

from apps.files_management.models import File
from apps.files_management.helpers import upload_file
from apps.files_management.helpers import uploaded_file_object_from_string
from apps.projects.models import Project
from apps.views_decorators import objects_exists, user_has_access

from .annotation_history_handler import AnnotationHistoryHandler
from .models import AnnotatingXmlContent


@login_required
@objects_exists
@user_has_access('RW')
def save(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == "PUT":
        file_symbol = '{0}_{1}'.format(project_id, file_id)

        try:
            annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=file_symbol)
        except AnnotatingXmlContent.DoesNotExist:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': 'There is no file to save with id: {0} for project: {1}.'.format(file_id, project_id),
                'data': None,
            }

            return JsonResponse(response, status=status)

        file = File.objects.get(id=file_id, deleted=False)
        file_version_old = file.version_number

        xml_content = annotating_xml_content.xml_content
        file_name = annotating_xml_content.file_name
        uploaded_file = uploaded_file_object_from_string(xml_content, file_name)

        project = Project.objects.get(id=project_id)
        upload_response = upload_file(uploaded_file, project, request.user, file.parent_dir)

        file_version_new = upload_response.version_number

        if file_version_old == file_version_new:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': 'There is no changes to save in file with id: {0}.'.format(file_id),
                'data': None,
            }

            return JsonResponse(response, status=status)

        else:
            status = HttpResponse.status_code

            response = {
                'status': status,
                'message': 'File with id: {0} was saved.'.format(file_id),
                'version': file_version_new,
                'data': None
            }

            return JsonResponse(response, status=status)


@login_required
@objects_exists
@user_has_access()
def history(request, project_id, file_id, version):  # type: (HttpRequest, int, int, int) -> HttpResponse
    if request.method == 'GET':
        annotation_history_handler = AnnotationHistoryHandler(project_id, file_id)
        history = annotation_history_handler.get_history(version)

        status = HttpResponse.status_code

        response = {
            'status': status,
            'message': 'OK',
            'data': history,
        }

        return JsonResponse(response, status=status)


@login_required
def current_user(request): # type: (HttpRequest) -> HttpResponse
    if request.method == 'GET':
        user = request.user

        status = HttpResponse.status_code

        response = {
            'id': 'person' + str(user.id),
            'forename': user.first_name,
            'surname': user.last_name,
            'email': user.email,
        }

        return JsonResponse(response, status=status)
