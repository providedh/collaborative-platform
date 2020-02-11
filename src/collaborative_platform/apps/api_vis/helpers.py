import copy
import re

from datetime import datetime
from lxml import etree

from django.http import HttpResponseBadRequest, HttpRequest, JsonResponse
from django.contrib.auth.models import User

import apps.index_and_search.models as es

from apps.api_vis.models import Clique, Commit, Entity, EventVersion, OrganizationVersion, PersonVersion, PlaceVersion, \
    CertaintyVersion, Unification, ObjectVersion
from apps.exceptions import BadRequest
from apps.files_management.models import Directory, File, FileMaxXmlIds, FileVersion
from apps.projects.models import Project, ProjectVersion


def search_files_by_person_name(request, project_id, query):  # type: (HttpRequest, int, str) -> JsonResponse
    r = es.Person.search().suggest('ac', query, completion={'field': 'suggest', 'fuzzy': True}).execute()

    response = set()
    for person in r.suggest.ac[0].options:
        person = person.to_dict()['_source']
        if person['project_id'] == project_id:
            file = File.objects.get(id=person['file_id'], deleted=False)
            response.add((file.name, file.get_path(), file.id))

    response = [{
        'name': p[0],
        'path': p[1],
        'id': p[2]
    } for p in response]

    return JsonResponse(response, safe=False)


def search_files_by_content(request, project_id, query):  # type: (HttpRequest, int, str) -> JsonResponse
    r = es.File.search().filter('term', project_id=project_id).query('match', text=query).execute()

    response = []
    for esfile in r:
        dbfile = File.objects.get(id=esfile.id, deleted=False)
        response.append({
            'name': dbfile.name,
            'path': dbfile.get_path(),
            'id': dbfile.id
        })

    return JsonResponse(response, safe=False)


def get_annotations_from_file_version_body(file_version, namespaces, annotation_tags):
    # type: (FileVersion, dict, list) -> list

    file_path = file_version.upload.path

    with open(file_path) as file:
        xml_content = file.read()

    annotations = []

    tree = etree.fromstring(xml_content)
    xml_body_node = tree.xpath('//default:text/default:body', namespaces=namespaces)[0]
    xml_certainties_node = tree.xpath('//default:teiHeader'
                                      '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                      namespaces=namespaces)[0]

    for annotation_tag in annotation_tags:
        annotation_nodes = xml_body_node.xpath('.//default:{0}'.format(annotation_tag), namespaces=namespaces)

        for ann_node in annotation_nodes:
            attributes = []
            uncertainties = []

            for ann_item in ann_node.attrib.items():
                attribute = reformat_attribute(ann_item, namespaces)
                attributes.append(attribute)

                # check if annotation have uncertainty
                regex = r'({.*?})*?id$'
                match = re.search(regex, ann_item[0])

                if match:
                    id_value = ann_item[1]
                    xml_uncertainties = xml_certainties_node.xpath(
                        './default:certainty[@target="#{0}"]'.format(id_value),
                        namespaces=namespaces)

                    for cert_node in xml_uncertainties:
                        cert_attributes = []

                        for cert_item in cert_node.attrib.items():
                            cert_attribute = reformat_attribute(cert_item, namespaces)
                            cert_attributes.append(cert_attribute)

                        description = cert_node.xpath('./default:description', namespaces=namespaces)

                        if description:
                            description = description.text

                        uncertainty = {
                            'tag': 'certainty',
                            'attributes': cert_attributes if cert_attributes else None,
                            'description': description if description else None,
                        }

                        uncertainties.append(uncertainty)

            annotation = {
                'tag': annotation_tag,
                'attributes': attributes if attributes else None,
                'textContext': ann_node.text if ann_node.text else None,
                'uncertainties': uncertainties if uncertainties else None,
            }

            annotations.append(annotation)

    return annotations


def reformat_attribute(item, namespaces):
    name = item[0]

    regex = r'{.*?}'
    match = re.search(regex, name)

    if match:
        for prefix, namespace in namespaces.items():
            ns = match.group()[1:-1]

            if namespace == ns:
                name = name.replace('{' + ns + '}', prefix + ':')

    attribute = {
        'name': name,
        'value': item[1]
    }

    return attribute


def create_entities_in_database(entities, project, file_version):  # type: (list, Project, FileVersion) -> None
    for entity in copy.deepcopy(entities):
        classes = {
            'person': PersonVersion,
            'org': OrganizationVersion,
            'event': EventVersion,
            'place': PlaceVersion,
            'certainty': CertaintyVersion,
            'object': ObjectVersion,
            'ingredient': ObjectVersion,
            'utensil': ObjectVersion,
            'productionMethod': ObjectVersion,
        }

        if entity['tag'] not in classes:
            continue

        entity["xml_id"] = entity.pop("id")
        try:
            entity_db = Entity.objects.get(
                project=project,
                file=file_version.file,
                xml_id=entity['xml_id'],
                type=entity['tag']
            )

        except Entity.DoesNotExist:
            entity_db = Entity.objects.create(
                project=project,
                file=file_version.file,
                xml_id=entity['xml_id'],
                created_in_version=file_version.number,
                type=entity['tag'],
            )

        tag = entity.pop("tag")

        # make sure we're not passing excessive keyword arguments to constructor, as that would cause an error
        tag_elements = {field.name for field in classes[tag]._meta.fields}
        excessive_elements = set(entity.keys()).difference(tag_elements)
        tuple(map(entity.pop, excessive_elements))  # pop all excessive elements from entity

        classes[tag](entity=entity_db, fileversion=file_version, **entity).save()


def fake_delete_entities(file, user):  # type: (File, User) -> list
    entities = Entity.objects.filter(
        file=file,
        deleted_on__isnull=True,
    )

    deleted_entity_ids = []

    file_version = FileVersion.objects.filter(
        file=file
    ).order_by('-number')[0].number

    for entity in entities:
        entity.deleted_in_version = file_version
        entity.deleted_on = datetime.now()
        entity.deleted_by = user
        entity.save()

        deleted_entity_ids.append(entity.id)

    return deleted_entity_ids


def fake_delete_unifications(file, user, deleted_entity_ids):  # type: (File, User, list) -> Commit
    unifications = Unification.objects.filter(
        entity_id__in=deleted_entity_ids,
        deleted_on__isnull=True,
    )

    if unifications:
        commit = Commit.objects.create(
            project_id=file.project_id,
            message=f"Removing unifications associated with deleted file '{file.name}'.",
        )

        for unification in unifications:
            file_version = FileVersion.objects.filter(
                file=file
            ).order_by('-number')[0]

            unification.deleted_on = datetime.now()
            unification.deleted_by = user
            unification.deleted_in_commit = commit
            unification.deleted_in_file_version = file_version
            unification.save()

        return commit


def validate_keys_and_types(request_data, required_name_type_template=None, optional_name_type_template=None,
                            parent_name=None):  # type: (dict, dict, dict, str) -> None
    if required_name_type_template:
        for key in required_name_type_template:
            if key not in request_data:
                if not parent_name:
                    raise BadRequest(f"Missing '{key}' parameter in request data.")
                else:
                    raise BadRequest(f"Missing '{key}' parameter in {parent_name} argument in request data.")

            if type(request_data[key]) is not required_name_type_template[key]:
                raise BadRequest(f"Invalid type of '{key}' parameter. "
                                 f"Correct type is: '{str(required_name_type_template[key])}'.")

    if optional_name_type_template:
        for key in optional_name_type_template:
            if key in request_data and type(request_data[key]) is not optional_name_type_template[key]:
                raise BadRequest(f"Invalid type of '{key}' parameter. "
                                 f"Correct type is: '{str(optional_name_type_template[key])}'.")


def get_file_id_from_path(project_id, file_path, parent_directory_id=None):  # type: (int, str, int) -> int
    splitted_path = file_path.split('/')

    if len(splitted_path) == 1:
        file_name = splitted_path[0]

        try:
            file = File.objects.get(
                project_id=project_id,
                parent_dir_id=parent_directory_id,
                name=file_name,
                deleted=False
            )

            return file.id

        except File.DoesNotExist:
            raise BadRequest(f"File with name {file_name} doesn't exist in this directory.")

    else:
        directory_name = splitted_path[0]

        try:
            directory = Directory.objects.get(project_id=project_id, parent_dir_id=parent_directory_id,
                                              name=directory_name)
            rest_of_path = '/'.join(splitted_path[1:])

            return get_file_id_from_path(project_id, rest_of_path, directory.id)

        except Directory.DoesNotExist:
            raise BadRequest(f"Directory with name {directory_name} does't exist in this directory.")


def get_entity_from_int_or_dict(request_entity, project_id):
    if type(request_entity) == int:
        try:
            entity = Entity.objects.get(
                id=request_entity,
                project_id=project_id
            )

            return entity

        except Entity.DoesNotExist:
            raise BadRequest(f"Entity with id: {request_entity} doesn't exist in project with id: {project_id}.")

    elif type(request_entity) == dict:
        required_keys = {
            'file_path': str,
            'xml_id': str,
        }

        validate_keys_and_types(request_entity, required_keys, parent_name="entity")

        file_path = request_entity['file_path']
        xml_id = request_entity['xml_id']

        file_id = get_file_id_from_path(project_id, file_path)

        try:
            entity = Entity.objects.get(
                project_id=project_id,
                file_id=file_id,
                xml_id=xml_id,
                deleted_on__isnull=True
            )

            return entity

        except Entity.DoesNotExist:
            file_name = request_entity['file_path'].split('/')[-1]
            raise BadRequest(f"Entity with xml:id: {xml_id} doesn't exist in file: {file_name}.")

    else:
        raise BadRequest(f"Invalid type of 'entity' parameter. Allowed types is '{str(int)}' and {str(dict)}.")


def parse_project_version(project_version):  # type: (str) -> (int, int)
    file_version_counter, commit_counter = str(project_version).split('.')
    file_version_counter = int(file_version_counter)
    commit_counter = int(commit_counter)

    return file_version_counter, commit_counter


def parse_query_string(query_string):
    parsed_query_string = {}

    types = query_string.get('types', None)
    types = parse_string_to_list_of_strings(types)
    parsed_query_string.update({'types': types})

    users = query_string.get('users', None)
    users = parse_string_to_list_of_integers(users)
    parsed_query_string.update({'users': users})

    date = query_string.get('date', None)
    date = parse_string_to_date(date)
    parsed_query_string.update({'date': date})

    start_date = query_string.get('start_date', None)
    start_date = parse_string_to_date(start_date)
    parsed_query_string.update({'start_date': start_date})

    end_date = query_string.get('end_date', None)
    end_date = parse_string_to_date(end_date)
    parsed_query_string.update({'end_date': end_date})

    file_version = query_string.get('file_version', None)
    file_version = parse_string_to_int(file_version)
    parsed_query_string.update({'file_version': file_version})

    project_version = query_string.get('project_version', None)
    project_version = parse_string_to_float(project_version)
    parsed_query_string.update({'project_version': project_version})

    return parsed_query_string


def parse_string_to_list_of_strings(string):
    if string:
        return string.split(',')


def parse_string_to_list_of_integers(string):
    if string:
        strings = string.split(',')
        integers = []

        for string in strings:
            integers.append(int(string))

        return integers


def parse_string_to_date(string):
    if string:
        return datetime.strptime(string, '%Y-%m-%d.%H.%M.%S')


def parse_string_to_int(string):
    if string:
        return int(string)


def parse_string_to_float(string):
    if string:
        return float(string)


def filter_unifications_by_project_version(unifications, project_id, project_version):
    file_version_counter, commit_counter = parse_project_version(project_version)

    try:
        project_version = ProjectVersion.objects.get(
            project_id=project_id,
            file_version_counter=file_version_counter,
            commit_counter=commit_counter,
        )
    except ProjectVersion.DoesNotExist:
        raise BadRequest(f"Version: {project_version} of project with id: {project_id} "
                         f"doesn't exist.")

    filtered_unifications = []

    for unification in unifications:
        created_in_file_version = unification.created_in_file_version.number

        try:
            deleted_in_file_version = unification.deleted_in_file_version.number
        except AttributeError:
            deleted_in_file_version = None

        file = unification.created_in_file_version.file

        try:
            file_version_in_project_version = FileVersion.objects.get(
                projectversion=project_version,
                file=file,
            ).number
        except FileVersion.DoesNotExist:
            continue

        if created_in_file_version <= file_version_in_project_version:
            if deleted_in_file_version and file_version_in_project_version <= deleted_in_file_version:
                filtered_unifications.append(unification)
            elif not deleted_in_file_version:
                filtered_unifications.append(unification)

    return filtered_unifications


def filter_entities_by_project_version(entities, project_id, project_version):
    file_version_counter, commit_counter = parse_project_version(project_version)

    try:
        project_version = ProjectVersion.objects.get(
            project_id=project_id,
            file_version_counter=file_version_counter,
            commit_counter=commit_counter,
        )
    except ProjectVersion.DoesNotExist:
        raise BadRequest(f"Version: {project_version} of project with id: {project_id} "
                         f"doesn't exist.")

    filtered_entities = []

    for entity in entities:
        created_in_file_version = entity.created_in_version
        deleted_in_file_version = entity.deleted_in_version
        file = entity.file

        try:
            file_version_in_project_version = FileVersion.objects.get(
                projectversion=project_version,
                file=file,
            ).number
        except FileVersion.DoesNotExist:
            continue

        if created_in_file_version <= file_version_in_project_version:
            if deleted_in_file_version and file_version_in_project_version < deleted_in_file_version:
                filtered_entities.append(entity)
            elif not deleted_in_file_version:
                filtered_entities.append(entity)

    return filtered_entities


def filter_entities_by_file_version(entities, project_id, file_id, file_version):
    try:
        file_version = FileVersion.objects.get(
            file_id=file_id,
            number=file_version,
        )

    except FileVersion.DoesNotExist:
        raise BadRequest(f"Version: {file_version} of file with id: {file_id} "
                         f"doesn't exist in project with id: {project_id}.")

    file_version = file_version.number

    filtered_entities = []

    for entity in entities:
        created_in_file_version = entity.created_in_version
        deleted_in_file_version = entity.deleted_in_version

        if created_in_file_version <= file_version:
            if deleted_in_file_version and file_version < deleted_in_file_version:
                filtered_entities.append(entity)
            elif not deleted_in_file_version:
                filtered_entities.append(entity)

    return filtered_entities


def common_filter_cliques(query_string, project_id):
    if query_string['project_version'] and query_string['date']:
        raise BadRequest("Provided timestamp parameters are ambiguous. Provide 'project_version' "
                         "for reference to specific project version, OR 'date' for reference to "
                         "latest project version on given time.")

    unifications = Unification.objects.filter(
        created_in_commit__isnull=False,
        project_id=project_id,
    )

    if query_string['types']:
        unifications = unifications.filter(entity__type__in=query_string['types'])

    if query_string['users']:
        unifications = unifications.filter(created_by_id__in=query_string['users'])

    if query_string['start_date']:
        unifications = unifications.filter(created_on__gte=query_string['start_date'])

    if query_string['end_date']:
        unifications = unifications.filter(created_on__lte=query_string['end_date'])

    if query_string['project_version']:
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

        unifications = filter_unifications_by_project_version(unifications, project_id, str(project_version))

    else:
        unifications = unifications.filter(deleted_on__isnull=True)

    cliques = {}

    for unification in unifications:
        if unification.clique_id not in cliques:
            clique = {
                'id': unification.clique_id,
                'name': unification.clique.asserted_name,
                'type': unification.entity.type,
                'entities': []
            }

            cliques.update({unification.clique_id: clique})

        cliques[unification.clique_id]['entities'].append(unification.entity_id)

    cliques = list(cliques.values())

    return cliques


def common_filter_entities(query_string, project_id):
    from apps.api_vis.api import ENTITY_CLASSES

    if query_string['project_version'] and query_string['date']:
        raise BadRequest("Provided timestamp parameters are ambiguous. Provide 'project_version' "
                         "for reference to specific project version, OR 'date' for reference to "
                         "latest project version on given time.")

    entities = Entity.objects.filter(project_id=project_id)

    if query_string['types']:
        entities = entities.filter(type__in=query_string['types'])

    # TODO: Update filtering by user after adding field for responsible user to entity model
    # if query_string['users']:
    #     entities = entities.filter()

    if query_string['project_version']:
        entities = filter_entities_by_project_version(entities, project_id, query_string['project_version'])

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
    else:
        entities = entities.filter(deleted_on__isnull=True)

    entities_to_return = []

    for entity in entities:
        if entity.type == 'certainty':
            continue

        entity_to_return = {
            'id': entity.id,
            'name': ENTITY_CLASSES[entity.type].objects.get(entity_id=entity.id).name,
            'type': entity.type,
        }

        entities_to_return.append(entity_to_return)

    return entities_to_return


def create_clique(request_data, project_id, user, created_in_annotator=False, ana='', description=''):
    # type: (dict, int, User, bool, str, str) -> (Clique, list)
    from apps.api_vis.api import ENTITY_CLASSES

    if (ana or description) and not created_in_annotator:
        raise BadRequest("'ana' and 'description' parameters are allowed only during unification in Annotator.")

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
        created_by=user,
        project_id=project_id,
        created_in_annotator=created_in_annotator,
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

            file_max_xml_ids = FileMaxXmlIds.objects.get(file=entity.file)
            file_max_xml_ids.certainty += 1
            file_max_xml_ids.save()

            Unification.objects.create(
                project_id=project_id,
                entity=entity,
                clique=clique,
                created_by=user,
                ana=ana,
                certainty=request_data['certainty'],
                description=description,
                created_in_file_version=file_version,
                created_in_annotator=created_in_annotator,
                xml_id=f'certainty_{entity.file.name}-{file_max_xml_ids.certainty}',
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

    return clique, unification_statuses
