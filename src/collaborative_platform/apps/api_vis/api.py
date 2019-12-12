import json
import xmltodict
import apps.index_and_search.models as es

from json.decoder import JSONDecodeError
from lxml import etree

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotModified

from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import File, FileVersion, FileMaxXmlIds
from apps.projects.helpers import user_is_project_admin
from apps.projects.models import Contributor, ProjectVersion
from apps.views_decorators import objects_exists, user_has_access

from .helpers import search_files_by_person_name, search_files_by_content, validate_keys_and_types, \
    get_annotations_from_file_version_body, get_entity_from_int_or_dict, parse_project_version, parse_query_string, \
    filter_entities_by_file_version, filter_entities_by_project_version, filter_unifications_by_project_version, \
    common_filter_cliques, common_filter_entities
from .models import Clique, CliqueToDelete, Commit, Entity, EventVersion, OrganizationVersion, PersonVersion, \
    PlaceVersion, Unification, UnificationToDelete


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
        response = { # TODO: not implemented
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
def project_cliques(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
                'project_version': float,
            }
            optional_keys = {'name': str}

            validate_keys_and_types(request_data, required_keys, optional_keys)

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
        try:
            query_string = parse_query_string(request.GET)

            cliques = common_filter_cliques(query_string, project_id)

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = cliques

            return JsonResponse(response, safe=False)

    elif request.method == 'DELETE':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'cliques': list,
                'project_version': float,
            }

            validate_keys_and_types(request_data, required_keys)

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
def clique_entities(request, project_id, clique_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'PUT':
        try:
            request_data = json.loads(request.body)

            required_keys = {
                'entities': list,
                'certainty': str,
                'project_version': float
            }

            validate_keys_and_types(request_data, required_keys)

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

            validate_keys_and_types(request_data, required_keys)

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

        unifications_to_remove = UnificationToDelete.objects.filter(
            deleted_by=request.user,
            project_version__project_id=project_id
        )

        for unification in unifications_to_remove:
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


@login_required
@objects_exists
@user_has_access('RW')
def commits(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'POST':
        try:
            cliques_to_create = Clique.objects.filter(
                created_by=request.user,
                created_in_commit=None,
                project_id=project_id,
            )

            cliques_to_delete = CliqueToDelete.objects.filter(
                deleted_by=request.user,
                project_version__project_id=project_id,
            )

            unifications_to_add = Unification.objects.filter(
                created_by=request.user,
                created_in_commit=None,
                project_id=project_id,
            )

            unifications_to_remove = UnificationToDelete.objects.filter(
                deleted_by=request.user,
                project_version__project_id=project_id
            )

            if len(cliques_to_create) == 0 and len(cliques_to_delete) == 0 and len(unifications_to_add) == 0 \
                    and len(unifications_to_remove) == 0:
                raise NotModified(f'You dont have any changes to commit in project with id: {project_id}.')

            request_data = json.loads(request.body)

            optional_keys = {
                'message': str,
            }

            validate_keys_and_types(request_data, optional_name_type_template=optional_keys)

            commit = Commit.objects.create(
                project_id=project_id,
                message=request_data['message'] if 'message' in request_data else ''
            )

            for clique_to_create in cliques_to_create:
                clique_to_create.created_in_commit = commit
                clique_to_create.save()

            for clique_to_delete in cliques_to_delete:
                clique = clique_to_delete.clique
                clique.deleted_on = clique_to_delete.deleted_on
                clique.deleted_by = clique_to_delete.deleted_by
                clique.deleted_in_commit = commit
                clique.save()

                unifications = Unification.objects.filter(
                    project_id=project_id,
                    clique=clique,
                    deleted_in_commit=None
                )

                for unification in unifications:
                    file_version = FileVersion.objects.get(
                        projectversion=clique_to_delete.project_version,
                        file=unification.entity.file,
                    )

                    unification.deleted_on = clique_to_delete.deleted_on
                    unification.deleted_by = clique_to_delete.deleted_by
                    unification.deleted_in_commit = commit
                    unification.deleted_in_file_version = file_version
                    unification.save()

                clique_to_delete.delete()

            for unification_to_add in unifications_to_add:
                unification_to_add.created_in_commit = commit

                file_max_xml_ids = FileMaxXmlIds.objects.get(file=unification_to_add.entity.file)
                file_max_xml_ids.certainty += 1
                file_max_xml_ids.save()

                unification_to_add.xml_id_number = file_max_xml_ids.certainty
                unification_to_add.save()

            for unification_to_remove in unifications_to_remove:
                unification = unification_to_remove.unification

                file_version = FileVersion.objects.get(
                    projectversion=unification_to_remove.project_version,
                    file=unification_to_remove.unification.entity.file,
                )

                unification.deleted_on = unification_to_remove.deleted_on
                unification.deleted_by = unification_to_remove.deleted_by
                unification.deleted_in_commit = commit
                unification.deleted_in_file_version = file_version
                unification.save()

                unification_to_remove.delete()

        except NotModified as exception:
            status = HttpResponseNotModified.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        except (BadRequest, JSONDecodeError) as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            status = HttpResponse.status_code

            response = {
                'status': status,
                'message': 'OK'
            }

            return JsonResponse(response)


@login_required
@objects_exists
@user_has_access()
def project_entities(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        try:
            query_string = parse_query_string(request.GET)

            entities = common_filter_entities(query_string, project_id)

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = entities

            return JsonResponse(response, safe=False)


@login_required
@objects_exists
@user_has_access()
def project_unbounded_entities(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    if request.method == 'GET':
        try:
            query_string = parse_query_string(request.GET)

            if query_string['project_version'] and query_string['date']:
                raise BadRequest("Provided timestamp parameters are ambiguous. Provide 'project_version' "
                                 "for reference to specific project version, OR 'date' for reference to "
                                 "latest project version on given time.")

            entities = Entity.objects.filter(
                project_id=project_id
            )

            unifications = Unification.objects.filter(
                created_in_commit__isnull=False,
                project_id=project_id,
            )

            if query_string['types']:
                entities = entities.filter(type__in=query_string['types'])
                unifications = unifications.filter(entity__type__in = query_string['types'])

            if query_string['users']:
                unifications = unifications.filter(created_by_id__in=query_string['users'])

            if query_string['start_date']:
                unifications = unifications.filter(created_on__gte=query_string['start_date'])

            if query_string['end_date']:
                unifications = unifications.filter(created_on__lte=query_string['end_date'])

            if query_string['project_version']:
                entities = filter_entities_by_project_version(entities, project_id, query_string['project_version'])
                unifications = filter_unifications_by_project_version(unifications, project_id,
                                                                      query_string['project_version'])

            elif query_string['date']:
                project_versions = ProjectVersion.objects.filter(
                    project_id=project_id,
                    date__lte=query_string['date'],
                ).order_by('-date')

                if project_versions:
                    project_version = project_versions[0]
                else:
                    raise BadRequest(f"There is no project version before date: {query_string['date']}.")

                entities = filter_entities_by_project_version(entities, project_id, str(project_version))
                unifications = filter_unifications_by_project_version(unifications, project_id, str(project_version))

            else:
                entities = entities.filter(deleted_on__isnull=True)
                unifications = unifications.filter(deleted_on__isnull=True)

            entities = [entity.id for entity in entities]
            bounded_entities = [unification.entity_id for unification in unifications]

            entities = set(entities)
            bounded_entities = set(bounded_entities)

            unbounded_entities = entities - bounded_entities
            unbounded_entities = Entity.objects.filter(id__in=unbounded_entities)

            entities_to_return = []

            for entity in unbounded_entities:
                if entity.type == 'certainty':
                    continue

                entity_to_return = {
                    'id': entity.id,
                    'name': ENTITY_CLASSES[entity.type].objects.get(entity_id=entity.id).name,
                    'type': entity.type,
                }

                entities_to_return.append(entity_to_return)

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = entities_to_return

            return JsonResponse(response, safe=False)


@login_required
@objects_exists
@user_has_access()
def file_cliques(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        try:
            query_string = parse_query_string(request.GET)

            cliques = common_filter_cliques(query_string, project_id)

            cliques_to_return = []

            for clique in cliques:
                for entity_id in clique['entities']:
                    entity = Entity.objects.get(id=entity_id)

                    if entity.file.id == file_id:
                        cliques_to_return.append(clique)
                        break

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = cliques_to_return

            return JsonResponse(response, safe=False)


@login_required
@objects_exists
@user_has_access()
def file_entities(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        try:
            query_string = parse_query_string(request.GET)

            entities = common_filter_entities(query_string, project_id)

            entities_to_return = []

            for entity_params in entities:
                entity = Entity.objects.get(id=entity_params['id'])

                if entity.file_id == file_id:
                    entities_to_return.append(entity_params)

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = entities_to_return

            return JsonResponse(response, safe=False)


def file_unbounded_entities(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        try:
            query_string = parse_query_string(request.GET)

            if query_string['file_version'] and query_string['date']:
                raise BadRequest("Provided timestamp parameters are ambiguous. Provide 'file_version' "
                                 "for reference to specific file version, OR 'date' for reference to "
                                 "latest file version on given time.")

            entities = Entity.objects.filter(
                project_id=project_id,
                file_id=file_id,
            )

            unifications = Unification.objects.filter(
                created_in_commit__isnull=False,
                project_id=project_id,
            )

            if query_string['types']:
                entities = entities.filter(type__in=query_string['types'])
                unifications = unifications.filter(entity__type__in=query_string['types'])

            if query_string['users']:
                unifications = unifications.filter(created_by_id__in=query_string['users'])

            if query_string['start_date']:
                unifications = unifications.filter(created_on__gte=query_string['start_date'])

            if query_string['end_date']:
                unifications = unifications.filter(created_on__lte=query_string['end_date'])

            if query_string['file_version']:
                entities = filter_entities_by_file_version(entities, project_id, file_id, query_string['file_version'])

            elif query_string['date']:
                project_versions = ProjectVersion.objects.filter(
                    project_id=project_id,
                    date__lte=query_string['date'],
                ).order_by('-date')

                if project_versions:
                    project_version = project_versions[0]

                    file_version = FileVersion.objects.get(
                        project_id=project_id,
                        file_id=file_id,
                        projectversion=project_version,
                    ).number

                else:
                    raise BadRequest(f"There is no file version before date: {query_string['date']}.")

                entities = filter_entities_by_file_version(entities, project_id, file_id, file_version)

            else:
                entities = entities.filter(deleted_on__isnull=True)

            entities = [entity.id for entity in entities]
            bounded_entities = [unification.entity_id for unification in unifications]

            entities = set(entities)
            bounded_entities = set(bounded_entities)

            unbounded_entities = entities - bounded_entities
            unbounded_entities = Entity.objects.filter(id__in=unbounded_entities)

            entities_to_return = []

            for entity in unbounded_entities:
                if entity.type == 'certainty':
                    continue

                entity_to_return = {
                    'id': entity.id,
                    'name': ENTITY_CLASSES[entity.type].objects.get(entity_id=entity.id).name,
                    'type': entity.type,
                }

                entities_to_return.append(entity_to_return)

        except BadRequest as exception:
            status = HttpResponseBadRequest.status_code

            response = {
                'status': status,
                'message': str(exception),
            }

            return JsonResponse(response, status=status)

        else:
            response = entities_to_return

            return JsonResponse(response, safe=False)