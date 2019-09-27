import re

import apps.index_and_search.models as es

from django.http import HttpRequest, JsonResponse
from lxml import etree

from apps.files_management.models import File, FileVersion


def search_files_by_person_name(request, project_id, query):  # type: (HttpRequest, int, str) -> JsonResponse
    r = es.Person.search().suggest('ac', query, completion={'field': 'suggest', 'fuzzy': True}).execute()

    response = set()
    for person in r.suggest.ac[0].options:
        person = person.to_dict()['_source']
        if person['project_id'] == project_id:
            file = File.objects.get(id=person['file_id'])
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
        dbfile = File.objects.get(id=esfile.id)
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
    xml_body_nodes = tree.xpath('//default:text/default:body', namespaces=namespaces)[0]

    for annotation_tag in annotation_tags:
        annotation_nodes = xml_body_nodes.xpath('.//default:{0}'.format(annotation_tag), namespaces=namespaces)

        for node in annotation_nodes:
            attributes = []

            for item in node.attrib.items():
                name = item[0]

                regex = r'{.*?}'
                match = re.search(regex, name)

                if match:
                    for prefix, namespace in namespaces.items():
                        ns = match.group()[1:-1]

                        if namespace == ns:
                            name = name.replace('{' + ns + '}', prefix + ':')

                atribute = {
                    'name': name,
                    'value': item[1]
                }

                attributes.append(atribute)

            annotation = {
                'tag': annotation_tag,
                'attributes': attributes,
                'textContext': node.text,
            }

            annotations.append(annotation)

    return annotations
