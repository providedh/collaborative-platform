from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseNotModified

from apps.files_management.file_conversions.ids_filler import IDsFiller
from apps.files_management.helpers import create_uploaded_file_object_from_string, overwrite_file, \
    extract_text_and_entities, index_entities, index_file
from apps.files_management.models import File
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
        version_nr_old = file.version_number

        xml_content = annotating_xml_content.xml_content
        file_name = annotating_xml_content.file_name

        ids_filler = IDsFiller(xml_content, file_name)
        is_id_filled = ids_filler.process()

        if is_id_filled:
            xml_content = ids_filler.text.read()

        uploaded_file = create_uploaded_file_object_from_string(xml_content, file_name)

        project = Project.objects.get(id=project_id)
        dbfile = File.objects.get(name=uploaded_file.name, parent_dir_id=file.parent_dir, project=project)
        file_overwrited = overwrite_file(dbfile, uploaded_file, request.user)

        version_nr_new = file_overwrited.version_number

        if version_nr_old == version_nr_new:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': 'There is no changes to save in file with id: {0}.'.format(file_id),
                'data': None,
            }

            return JsonResponse(response, status=status)

        else:
            text, entities = extract_text_and_entities(xml_content, project.id, file_overwrited.id)
            index_entities(entities)
            index_file(dbfile, text)

            status = HttpResponse.status_code

            response = {
                'status': status,
                'message': 'File with id: {0} was saved.'.format(file_id),
                'version': version_nr_new,
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
