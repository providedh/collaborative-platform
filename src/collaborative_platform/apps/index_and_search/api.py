from json import dumps
from elasticsearch_dsl import Search

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse, HttpResponse

from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def entity_completion(request, project_id, entity_type, query):  # type: (HttpRequest, int, str, str) -> HttpResponse
    if entity_type not in ('person', 'event', 'place', 'organization'):
        return HttpResponseBadRequest(dumps({"message": "Invalid entity type"}))
    r = Search(index=entity_type).suggest('ac', query, completion={'field': 'suggest', 'fuzzy': True}).execute()
    result = {
        'data': [entity.to_dict() for entity in r.suggest.ac[0].options if
                 entity['_source']['project_id'] == project_id]
    }
    return JsonResponse(result)
