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
from apps.projects.models import Contributor, ProjectVersion
from apps.views_decorators import objects_exists, user_has_access

from .helpers import search_files_by_person_name, search_files_by_content, validate_keys_and_types, \
    get_annotations_from_file_version_body, get_entity_from_int_or_dict, parse_project_version
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
                'project_version': float,
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

            file_version_counter, commit_counter = parse_project_version(request_data['project_version'])

            try:
                project_version = ProjectVersion.objects.get(
                    project_id=project_id,
                    file_version_counter=file_version_counter,
                    commit_counter=commit_counter,
                )
            except ProjectVersion.DoesNotExist:
                raise BadRequest(f"Version: {request_data['project_version']} of project with id: {project_id} "
                                 f"doesn't exist.")

            unification_statuses = []

            for i, entity in enumerate(request_data['entities']):
                if type(entity) == int:
                    unification_statuses.append({'id': entity})
                else:
                    unification_statuses.append(entity)

                try:
                    entity = get_entity_from_int_or_dict(entity, project_id)

                    try:
                        file_version = FileVersion.objects.get(
                            projectversion=project_version,
                            file=entity.file
                        )
                    except FileVersion.DoesNotExist:
                        raise BadRequest(f"Source file of entity with id: {entity.id} doesn't exist in version: "
                                         f"{request_data['project_version']} of the project with id: {project_id}.")

                    if entity.created_in_version > file_version.number or \
                            entity.deleted_in_version and entity.deleted_in_version < file_version.number:
                        raise BadRequest(f"Entity with id: {entity.id} doesn't exist in version: "
                                         f"{request_data['project_version']} of the project with id: {project_id}.")

                    Unification.objects.create(
                        project_id=project_id,
                        entity=entity,
                        clique=clique,
                        created_by=request.user,
                        certainty=request_data['certainty'],
                        created_in_file_version=file_version,
                    )

                    unification_statuses[i].update({
                        'status': 200,
                        'message': 'OK'
                    })

                except BadRequest as exception:
                    status = HttpResponseBadRequest.status_code

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
            response = {
                'name': clique.asserted_name,
                'id': clique.id,
                'unification_statuses': unification_statuses,
            }

            return JsonResponse(response)

    elif request.method == 'GET':
        pass

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'cliques': list,
                'project_version': float,
            }

            validate_keys_and_types(required_keys, request_data)

            if len(request_data['cliques']) == 0:
                raise NotModified("You didn't provide any clique id to delete.")

            file_version_counter, commit_counter = parse_project_version(request_data['project_version'])

            try:
                project_version = ProjectVersion.objects.get(
                    project_id=project_id,
                    file_version_counter=file_version_counter,
                    commit_counter=commit_counter,
                )
            except ProjectVersion.DoesNotExist:
                raise BadRequest(f"Version: {request_data['project_version']} of project with id: {project_id} "
                                 f"doesn't exist.")

            delete_statuses = []

            for i, clique_id in enumerate(request_data['cliques']):
                delete_statuses.append({'id': clique_id})

                try:
                    try:
                        clique = Clique.objects.get(
                            project_id=project_id,
                            id=clique_id
                        )
                    except Clique.DoesNotExist:
                        raise BadRequest(f"There is no clique with id: {clique_id} in project: {project_id}.")

                    if request.user != clique.created_by and not user_is_project_admin(project_id, request.user):
                        raise BadRequest(f"You don't have enough permissions to delete another user's clique.")

                    try:
                        CliqueToDelete.objects.get(
                            clique=clique,
                            deleted_by=request.user,
                        )
                    except CliqueToDelete.DoesNotExist:
                        CliqueToDelete.objects.create(
                            clique=clique,
                            deleted_by=request.user,
                            project_version=project_version,
                        )
                    else:
                        raise NotModified(f"You already deleted clique with id: {clique_id}.")

                    delete_statuses[i].update({
                        'status': 200,
                        'message': 'OK'
                    })

                except BadRequest as exception:
                    status = HttpResponseBadRequest.status_code

                    delete_statuses[i].update({
                        'status': status,
                        'message': str(exception)
                    })

                except NotModified as exception:
                    status = HttpResponseNotModified.status_code

                    delete_statuses[i].update({
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

        except NotModified as exception:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {'delete_statuses': delete_statuses}

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def entities(request, project_id, clique_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
                'project_version': float
            }

            validate_keys_and_types(required_keys, request_data)

            if not request_data['entities']:
                raise BadRequest("Provide at least one entity.")

            clique = Clique.objects.get(
                project_id=project_id,
                id=clique_id
            )

            file_version_counter, commit_counter = parse_project_version(request_data['project_version'])

            try:
                project_version = ProjectVersion.objects.get(
                    project_id=project_id,
                    file_version_counter=file_version_counter,
                    commit_counter=commit_counter,
                )
            except ProjectVersion.DoesNotExist:
                raise BadRequest(f"Version: {request_data['project_version']} of project with id: {project_id} "
                                 f"doesn't exist.")

            unification_statuses = []

            for i, entity in enumerate(request_data['entities']):
                if type(entity) == int:
                    unification_statuses.append({'id': entity})
                else:
                    unification_statuses.append(entity)

                try:
                    entity = get_entity_from_int_or_dict(entity, project_id)

                    try:
                        file_version = FileVersion.objects.get(
                            projectversion=project_version,
                            file=entity.file,
                        )
                    except FileVersion.DoesNotExist:
                        raise BadRequest(f"Source file of entity with id: {entity.id} doesn't exist in version: "
                                         f"{request_data['project_version']} of the project with id: {project_id}.")

                    if entity.created_in_version > file_version.number or \
                            entity.deleted_in_version and entity.deleted_in_version < file_version.number:
                        raise BadRequest(f"Entity with id: {entity.id} doesn't exist in version: "
                                         f"{request_data['project_version']} of the project with id: {project_id}.")

                    try:
                        Unification.objects.get(
                            project_id=project_id,
                            entity=entity,
                            clique=clique,
                            created_by=request.user,
                        )
                    except Unification.DoesNotExist:
                        Unification.objects.create(
                            project_id=project_id,
                            entity=entity,
                            clique=clique,
                            created_by=request.user,
                            certainty=request_data['certainty'],
                            created_in_file_version=file_version,
                        )
                    else:
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

    elif request.method == 'GET':
        pass

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'project_version': float
            }

            validate_keys_and_types(required_keys, request_data)

            if len(request_data['entities']) == 0:
                raise NotModified("You didn't provide any entity id to remove.")

            file_version_counter, commit_counter = parse_project_version(request_data['project_version'])

            try:
                project_version = ProjectVersion.objects.get(
                    project_id=project_id,
                    file_version_counter=file_version_counter,
                    commit_counter=commit_counter,
                )
            except ProjectVersion.DoesNotExist:
                raise BadRequest(f"Version: {request_data['project_version']} of project with id: {project_id} "
                                 f"doesn't exist.")

            delete_statuses = []

            for i, entity_id in enumerate(request_data['entities']):
                delete_statuses.append({'id': entity_id})

                try:
                    try:
                        unification = Unification.objects.get(
                            project_id=project_id,
                            clique_id=clique_id,
                            entity_id=entity_id,
                        )
                    except Unification.DoesNotExist:
                        raise BadRequest(f"There is no entity with id: {entity_id} in clique with id: {clique_id} "
                                         f"in project: {project_id}.")

                    if request.user != unification.created_by and not user_is_project_admin(project_id, request.user):
                        raise BadRequest(f"You don't have enough permissions to remove another user's entity "
                                         f"from clique.")

                    try:
                        UnificationToDelete.objects.get(
                            unification=unification,
                            deleted_by=request.user,
                        )
                    except UnificationToDelete.DoesNotExist:
                        UnificationToDelete.objects.create(
                            unification=unification,
                            deleted_by=request.user,
                            project_version=project_version,
                        )
                    else:
                        raise NotModified(f"You already removed entity with id: {entity_id} from clique "
                                          f"with id: {clique_id}.")

                    delete_statuses[i].update({
                        'status': 200,
                        'message': 'OK'
                    })

                except BadRequest as exception:
                    status = HttpResponseBadRequest.status_code

                    delete_statuses[i].update({
                        'status': status,
                        'message': str(exception)
                    })

                except NotModified as exception:
                    status = HttpResponseNotModified.status_code

                    delete_statuses[i].update({
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

        except NotModified as exception:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = {'delete_statuses': delete_statuses}

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access('RW')
def uncommitted_changes(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        uncommitted_changes = {
            'cliques_to_create': [],
            'cliques_to_delete': [],
            'unification_to_add': [],
            'unification_to_remove': [],
        }

        cliques_to_create = Clique.objects.filter(
            created_by=request.user,
            created_in_commit=None,
            project_id=project_id,
        )

        for clique in cliques_to_create:
            clique_data = {
                'id': clique.id,
                'asserted_name': clique.asserted_name,
                'created_by_id': clique.created_by_id,
            }

            uncommitted_changes['cliques_to_create'].append(clique_data)

        cliques_to_delete = CliqueToDelete.objects.filter(
            deleted_by=request.user,
            project_version__project_id=project_id,
        )

        for clique in cliques_to_delete:
            clique_data = {
                'id': clique.id,
                'asserted_name': clique.clique.asserted_name,
                'created_by_id': clique.clique.created_by,
            }

            uncommitted_changes['cliques_to_delete'].append(clique_data)

        unifications_to_add = Unification.objects.filter(
            created_by=request.user,
            created_in_commit=None,
            project_id=project_id,
        )

        for unification in unifications_to_add:
            unification_data = {
                'id': unification.id,
                'clique_id': unification.clique.id,
                'clique_asserted_name': unification.clique.asserted_name,
                'entity_id': unification.entity_id,
                'entity_name': ENTITY_CLASSES[unification.entity.type].objects.get(
                    entity_id=unification.entity_id).name,
                'certainty': unification.certainty,
                'created_by': unification.created_by_id,
            }

            uncommitted_changes['unification_to_add'].append(unification_data)

        unifications_to_delete = UnificationToDelete.objects.filter(
            deleted_by=request.user,
            project_version__project_id=project_id
        )

        for unification in unifications_to_delete:
            unification_data = {
                'id': unification.unification.id,
                'clique_id': unification.unification.clique_id,
                'clique_asserted_name': unification.unification.clique.asserted_name,
                'entity_id': unification.unification.entity_id,
                'entity_name': ENTITY_CLASSES[unification.unification.entity.type].objects.get(
                    entity_id=unification.unification.entity_id).name,
                'certainty': unification.unification.certainty,
                'created_by': unification.unification.created_by_id,
            }

            uncommitted_changes['unification_to_remove'].append(unification_data)

        response = {'uncommitted_changes': uncommitted_changes}

        return JsonResponse(response)
