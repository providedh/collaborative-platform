import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseNotModified

# from apps.api_vis.helpers import create_entities_in_database
from apps.api_vis.models import Clique, Commit, Unification
from apps.files_management.file_conversions.ids_filler import IDsFiller
from apps.files_management.helpers import create_uploaded_file_object_from_string, overwrite_file, \
    extract_text_and_entities, index_entities, index_file
from apps.files_management.models import File, FileVersion
from apps.projects.models import Project
from apps.views_decorators import objects_exists, user_has_access

from .annotation_history_handler import AnnotationHistoryHandler
from .models import AnnotatingXmlContent


logger = logging.getLogger('annotator')


@login_required
@objects_exists
@user_has_access('RW')
def save(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == "PUT":
        file_symbol = '{0}_{1}'.format(project_id, file_id)

        file = File.objects.get(id=file_id, deleted=False)
        version_nr_old = file.version_number

        logger.info(f"Get request from user: '{request.user.username}' to save a file: '{file.name}' "
                    f"in room: '{file_symbol}'")

        try:
            annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=file_symbol)
        except AnnotatingXmlContent.DoesNotExist:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': 'There is no file to save with id: {0} for project: {1}.'.format(file_id, project_id),
                'data': None,
            }

            logger.error(f"Saving file '{file.name}' in room: '{file_symbol}' failed")
            logger.error(f"Send response to user: '{request.user.username}' with content: '{json.dumps(response)}")

            return JsonResponse(response, status=status)

        xml_content = annotating_xml_content.xml_content
        file_name = annotating_xml_content.file_name

        ids_filler = IDsFiller(xml_content, file_name, file_id)
        is_id_filled = ids_filler.process()

        if is_id_filled:
            xml_content = ids_filler.text.read()

        uploaded_file = create_uploaded_file_object_from_string(xml_content, file_name)

        project = Project.objects.get(id=project_id)
        dbfile = File.objects.get(name=uploaded_file.name, parent_dir_id=file.parent_dir, project=project,
                                  deleted=False)
        file_overwrited = overwrite_file(dbfile, uploaded_file, request.user)

        version_nr_new = file_overwrited.version_number

        unifications = Unification.objects.filter(
            deleted_on__isnull=True,
            created_by=request.user,
            created_in_commit__isnull=True,
            created_in_annotator=True,
        )

        if version_nr_old == version_nr_new and not unifications:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': 'There is no changes to save in file with id: {0}.'.format(file_id),
                'data': None,
            }

            logger.error(f"Saving file '{file.name}' in room: '{file_symbol}' failed")
            logger.error(f"Send response to user: '{request.user.username}' with content: '{json.dumps(response)}")

            return JsonResponse(response, status=status)

        if version_nr_old < version_nr_new or unifications:
            message = ''

            if version_nr_old < version_nr_new:
                text, entities = extract_text_and_entities(xml_content, project.id, file_overwrited.id)
                file_version = FileVersion.objects.get(file=file_overwrited, number=file_overwrited.version_number)
                # create_entities_in_database(entities, project, file_version)
                index_entities(entities)
                index_file(dbfile, text)

                message += f"File with id: {file_id} was saved."

            if unifications:
                commit = Commit.objects.create(
                    project=project,
                    message="Commit created in Annotator."
                )

                cliques_ids = unifications.values_list('clique_id', flat=True)
                cliques_ids = set(cliques_ids)

                for unification in unifications:
                    unification.created_in_commit = commit
                    unification.save()

                cliques = Clique.objects.filter(
                    deleted_on__isnull=True,
                    created_by=request.user,
                    created_in_commit__isnull=True,
                    created_in_annotator=True,
                    id__in=cliques_ids,
                )

                for clique in cliques:
                    clique.created_in_commit = commit
                    clique.save()

                if message:
                    message += ' '

                message += f"New commit with {len(unifications)} unifications was created."

            status = HttpResponse.status_code

            response = {
                'status': status,
                'message': message,
                'version': version_nr_new,
                'data': None
            }

            logger.info(f"Successfully saved file '{file.name}' in room: '{file_symbol}'. "
                        f"New file version is: '{version_nr_new}'")
            logger.info(f"Send response to user: '{request.user.username}' with content: '{json.dumps(response)}")

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
