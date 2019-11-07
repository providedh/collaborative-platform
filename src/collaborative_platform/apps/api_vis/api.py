import json
import xmltodict
import apps.index_and_search.models as es

from json.decoder import JSONDecodeError
from lxml import etree

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotModified

from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import File, FileVersion
from apps.projects.helpers import user_is_project_admin
from apps.projects.models import Contributor
from apps.views_decorators import objects_exists, user_has_access

from .helpers import search_files_by_person_name, search_files_by_content, validate_keys_and_types, \
    get_annotations_from_file_version_body, get_entity_from_int_or_dict
from .models import Clique, CliqueToDelete, EventVersion, OrganizationVersion, PersonVersion, PlaceVersion, \
    Unification, UnificationToDelete


NAMESPACES = {
    'default': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xi': 'http://www.w3.org/2001/XInclude',
}

ANNOTATION_TAGS = ['date', 'event', 'location', 'geolocation', 'name', 'occupation', 'object', 'org', 'person', 'place',
                   'country', 'time']


ENTITY_CLASSES = {
    'event': EventVersion,
    'org': OrganizationVersion,
    'person': PersonVersion,
    'place': PlaceVersion,
}


@login_required
def projects(request):  # type: (HttpRequest) -> JsonResponse
    if request.method == 'GET':
        user = request.user

        contributors = Contributor.objects.filter(user=user)

        response = []

        for contributor in contributors:
            project = {
                'id': contributor.project.id,
                'name': contributor.project.title,
                'permissions': contributor.permissions,
            }

            response.append(project)

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def project_history(request, project_id):  # type: (HttpRequest, int) -> JsonResponse
    if request.method == 'GET':
        response = {
            'info': 'Not implemented. Need to agree an appearance of response.'
        }

        return JsonResponse(response, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def project_files(request, project_id):  # type: (HttpRequest, int) -> JsonResponse
    if request.method == 'GET':
        search = request.GET.get('search', None)
        person = request.GET.get('person', None)

        if search:
            return search_files_by_content(request, project_id, search)

        elif person:
            return search_files_by_person_name(request, project_id, person)

        else:
            files = File.objects.filter(project=project_id, deleted=False).order_by('id')

            response = []

            for file in files:
                file_details = {
                    'id': file.id,
                    'name': file.name,
                    'path': file.get_relative_path(),
                }

                response.append(file_details)

            return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def file(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        response = file.download()

        return response


@login_required
@objects_exists
@user_has_access()
def file_body(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        file_version = FileVersion.objects.get(file=file, number=file.version_number)
        file_path = file_version.upload.path

        with open(file_path) as file:
            xml_content = file.read()

        tree = etree.fromstring(xml_content)
        body = tree.xpath('//default:text/default:body', namespaces=NAMESPACES)[0]
        text_nodes = body.xpath('.//text()')
        plain_text = ''.join(text_nodes)

        return HttpResponse(plain_text, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def file_meta(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        file_version = FileVersion.objects.get(file=file, number=file.version_number)
        file_path = file_version.upload.path

        with open(file_path) as file:
            xml_content = file.read()

        parsed_xml = xmltodict.parse(xml_content)
        response = parsed_xml['TEI']['teiHeader']

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def file_names(request, project_id, file_id):  # type: (HttpRequest, int, int) -> JsonResponse
    if request.method == 'GET':
        response = {
            'info': 'Not implemented.'
        }

        return JsonResponse(response, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def file_annotations(request, project_id, file_id):  # type: (HttpRequest, int, int) -> JsonResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        file_version = FileVersion.objects.get(file=file, number=file.version_number)

        annotations = get_annotations_from_file_version_body(file_version, NAMESPACES, ANNOTATION_TAGS)

        return JsonResponse(annotations, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def file_people(request, project_id, file_id):  # type: (HttpRequest, int, int) -> JsonResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        file_version = FileVersion.objects.get(file=file, number=file.version_number)

        annotation_tags = ['persName', 'person', 'name']

        annotations = get_annotations_from_file_version_body(file_version, NAMESPACES, annotation_tags)

        return JsonResponse(annotations, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def context_search(request, project_id, text):  # type: (HttpRequest, int, str) -> HttpResponse
    r = es.File.search().filter('term', project_id=project_id).highlight('text').query('match', text=text).execute()

    response = []
    for hit in r:
        file = File.objects.get(id=hit.id, deleted=False)
        response.append({
            'file': {
                'name': file.name,
                'path': file.get_path(),
                'id': file.id
            },
            'contexts': [fragment for fragment in hit.meta.highlight.text]
        })

    return JsonResponse(response, safe=False)


@login_required
@objects_exists
@user_has_access('RW')
def cliques(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
            }
            optional_keys = {'name': str}

            validate_keys_and_types(required_keys, request_data, optional_keys)

            if 'name' in request_data and request_data['name'] != '':
                clique_name = request_data['name']
            elif len(request_data['entities']) > 0:
                request_entity = request_data['entities'][0]
                entity = get_entity_from_int_or_dict(request_entity, project_id)
                entity_version = ENTITY_CLASSES[entity.type].objects.filter(entity=entity).order_by('-fileversion')[0]
                clique_name = entity_version.name
            else:
                raise BadRequest(f"Missing name for a clique. Provide name in 'name' parameter or at least one entity.")

            clique = Clique.objects.create(
                asserted_name=clique_name,
                created_by=request.user,
                project_id=project_id,
            )

            for entity in request_data['entities']:
                entity_id = get_entity_from_int_or_dict(entity, project_id).id

                Unification.objects.create(
                    project_id=project_id,
                    entity_id=entity_id,
                    clique=clique,
                    created_by=request.user,
                    certainty=request_data['certainty'],
                )

        except (BadRequest, JSONDecodeError) as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {
                'name': clique.asserted_name,
                'id': clique.id,
            }

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def add_to_clique(request, project_id, clique_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
            }

            validate_keys_and_types(required_keys, request_data)

            if not request_data['entities']:
                raise BadRequest("Provide at least one entity.")

            clique = Clique.objects.get(project_id=project_id, id=clique_id)
            unification_statuses = []

            for i, entity in enumerate(request_data['entities']):
                if type(entity) == int:
                    unification_statuses.append({'id': entity})
                else:
                    unification_statuses.append(entity)

                try:
                    entity_id = get_entity_from_int_or_dict(entity, project_id).id

                    unification, created = Unification.objects.get_or_create(
                        project_id=project_id,
                        entity_id=entity_id,
                        clique=clique,
                        created_by=request.user,
                        certainty=request_data['certainty']
                    )

                    if not created:
                        raise NotModified(f"This entity already exist in clique with id: {clique_id}")

                    unification_statuses[i].update({
                        'status': 200,
                        'message': 'OK'
                    })

                except (BadRequest, JSONDecodeError) as exception:
                    status = HttpResponseBadRequest.status_code

                    unification_statuses[i].update({
                        'status': status,
                        'message': str(exception)
                    })
                except NotModified as exception:
                    status = HttpResponseNotModified.status_code

                    unification_statuses[i].update({
                        'status': status,
                        'message': str(exception)
                    })

        except (BadRequest, JSONDecodeError) as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {'unification_statuses': unification_statuses}

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def clique(request, project_id, clique_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'DELETE':
        try:
            try:
                clique = Clique.objects.get(
                    project_id=project_id,
                    id=clique_id,
                )

            except Clique.DoesNotExist:
                raise BadRequest(f"There is no clique with id: {clique_id} in project: {project_id}.")

            if request.user != clique.created_by and not user_is_project_admin(project_id, request.user):
                raise BadRequest(f"You don't have enough permissions to delete another user's clique.")

            clique_to_delete, created = CliqueToDelete.objects.get_or_create(
                clique=clique,
                deleted_by=request.user,
            )

            if not created:
                raise NotModified(f"You already deleted clique with id: {clique_id}.")

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        except NotModified as exception:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': str(exception)
            }

            return JsonResponse(response, status=status)

        else:
            response = {}

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def entities_in_clique(request, project_id, clique_id, entity_id):  # type: (HttpRequest, int, int, int) -> HttpResponse
    if request.method == 'DELETE':
        try:
            try:
                unification = Unification.objects.get(
                    project_id=project_id,
                    entity_id=entity_id,
                    clique_id=clique_id,
                )

            except Unification.DoesNotExist:
                raise BadRequest(f"There is no entity with id: {entity_id} in clique: {clique_id} "
                                 f"in project: {project_id}.")

            if request.user != unification.created_by and not user_is_project_admin(project_id, request.user):
                raise BadRequest("You don't have enough permissions to remove entity added by another user.")

            unification_to_delete, created = UnificationToDelete.objects.get_or_create(
                unification=unification,
                deleted_by=request.user,
            )

            if not created:
                raise NotModified(f"You already removed entity with id: {entity_id} from clique with id: {clique_id}.")

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        except NotModified as exception:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {}

            return JsonResponse(response)
