from django.http import HttpRequest, JsonResponse

from apps.files_management.models import File
from apps.index_and_search.models import Person


def search_files_by_person_name(request, project_id, query):  # type: (HttpRequest, int, str) -> JsonResponse
    r = Person.search().suggest('ac', query, completion={'field': 'suggest', 'fuzzy': True}).execute()

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
