from dateutil import parser

from django.http import HttpRequest, JsonResponse

import apps.index_and_search.models as es

from apps.files_management.models import File


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


def parse_project_version(project_version):  # type: (str) -> (int, int)
    file_version_counter, commit_counter = str(project_version).split('.')
    file_version_counter = int(file_version_counter)
    commit_counter = int(commit_counter)

    return file_version_counter, commit_counter


def parse_query_string(query_string):
    parsed_query_string = {}

    types = query_string.get('types', None)

    if types:
        types = parse_string_to_list_of_strings(types)
        parsed_query_string.update({'types': types})

    users = query_string.get('users', None)

    if users:
        users = parse_string_to_list_of_integers(users)
        parsed_query_string.update({'users': users})

    date = query_string.get('date', None)

    if date:
        date = parse_string_to_date(date)
        parsed_query_string.update({'date': date})

    start_date = query_string.get('start_date', None)

    if start_date:
        start_date = parse_string_to_date(start_date)
        parsed_query_string.update({'start_date': start_date})

    end_date = query_string.get('end_date', None)

    if end_date:
        end_date = parse_string_to_date(end_date)
        parsed_query_string.update({'end_date': end_date})

    file_version = query_string.get('file_version', None)

    if file_version:
        file_version = parse_string_to_int(file_version)
        parsed_query_string.update({'file_version': file_version})

    project_version = query_string.get('project_version', None)

    if project_version:
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
        return parser.parse(string)


def parse_string_to_int(string):
    if string:
        return int(string)


def parse_string_to_float(string):
    if string:
        return float(string)
