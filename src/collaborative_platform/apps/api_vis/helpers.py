import re

import apps.index_and_search.models as es

from django.http import HttpRequest, JsonResponse
from lxml import etree

from apps.api_vis.models import Entity, EventVersion, OrganizationVersion, PersonVersion, PlaceVersion
from apps.files_management.models import File, FileVersion, Project, Directory


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
                    xml_uncertainties = xml_certainties_node.xpath('./default:certainty[@target="#{0}"]'.format(id_value),
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
    for entity in entities:
        try:
            entity_db = Entity.objects.get(
                project=project,
                file=file_version.file,
                xml_id=entity['id'],
                type=entity['tag']
            )

            entity_db.last_existed_in_version = file_version.number
            entity_db.save()

        except Entity.DoesNotExist:
            entity_db = Entity.objects.create(
                project=project,
                file=file_version.file,
                xml_id=entity['id'],
                added_in_version=file_version.number,
                last_existed_in_version=file_version.number,
                type=entity['tag'],
            )

        if entity['tag'] == 'person':
            person_version = PersonVersion.objects.create(
                entity=entity_db,
                fileversion=file_version,
                name=entity['name'],
                xml=entity['xml'] if 'xml' in entity else None,
                context=entity['context'] if 'context' in entity else None,
                forename=entity['forename'],
                surname=entity['surname'],
            )
        elif entity['tag'] == 'org':
            organisation_version = OrganizationVersion.objects.create(
                entity=entity_db,
                fileversion=file_version,
                name=entity['name'],
                xml=entity['xml'] if 'xml' in entity else None,
                context=entity['context'] if 'context' in entity else None,
            )
        elif entity['tag'] == 'event':
            event_version = EventVersion.objects.create(
                entity=entity_db,
                fileversion=file_version,
                name=entity['name'],
                xml=entity['xml'] if 'xml' in entity else None,
                context=entity['context'] if 'context' in entity else None,
                date=entity['date'] if 'date' in entity else None,
            )
        elif entity['tag'] == 'place':
            place_version = PlaceVersion.objects.create(
                entity=entity_db,
                fileversion=file_version,
                name=entity['name'],
                xml=entity['xml'] if 'xml' in entity else None,
                context=entity['context'] if 'context' in entity else None,
                location=entity['location'] if 'location' in entity else None,
                country=entity['country'] if 'country' in entity else None
            )


def validate_request_parameters(name_type_template, request_data):  # type: (dict, dict) -> (bool, str)
    message = ""
    correct = True

    for key in name_type_template:
        if key not in request_data:
            message = f"Missing '{key}' parameter in request data."
            correct = False
            break

        if type(request_data[key]) is not name_type_template[key]:
            message = f"Invalid type of '{key}' parameter. Correct type is '{str(name_type_template[key])}'"
            correct = False
            break

    return correct, message


def get_file_id_from_path(project_id, file_path, parent_directory_id=None):  # type: (int, str, int) -> int
    splitted_path = file_path.split('/')

    if len(splitted_path) == 1:
        file_name = splitted_path[0]
        file = File.objects.get(project_id=project_id, parent_dir_id=parent_directory_id, name=file_name)

        return file.id

    else:
        direcory_name = splitted_path[0]
        directory = Directory.objects.get(project_id=project_id, parent_dir_id=parent_directory_id, name=direcory_name)
        rest_of_path = '/'.join(splitted_path[1:])

        return get_file_id_from_path(project_id, rest_of_path, directory.id)


def get_entity_from_int_or_dict(request_entity, project_id):
    if type(request_entity) == int:
        entity = Entity.objects.get(id=request_entity)
    else:
        file_path = request_entity['file_path']
        xml_id = request_entity['xml_id']

        file_id = get_file_id_from_path(project_id, file_path)
        entity = Entity.objects.get(file_id=file_id, xml_id=xml_id)

    return entity
