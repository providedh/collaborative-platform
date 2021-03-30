from json import dumps
from elasticsearch_dsl import Search

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse, HttpResponse

from apps.files_management.models import File
from .models import User
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def entity_completion(request, project_id, entity_type, query):  # type: (HttpRequest, int, str, str) -> HttpResponse
    entity_type = entity_type.lower()
    if entity_type not in ('person', 'event', 'place', 'organization', 'ingredient', 'utensil', 'productionmethod'):
        return HttpResponseBadRequest(dumps({"message": "Invalid entity type"}))
    r = Search(index=entity_type).suggest('ac', query, completion={'field': 'suggest', 'fuzzy': True}).execute()
    result = {
        'data': [entity.to_dict() for entity in r.suggest.ac[0].options if
                 entity['_source']['project_id'] == project_id]
    }
    for entry in result['data']:
        entry['_source']['filepath'] = File.objects.get(id=entry['_source']['file_id'], deleted=False).get_path()

    return JsonResponse(result)


@login_required
def search_user(request, query):  # type: (HttpRequest, str) -> HttpResponse
    r = User.search().suggest('ac', query, completion={'field': 'suggest', 'fuzzy': True}).execute()
    result = {
        'data': [user.to_dict() for user in r.suggest.ac[0].options]
    }
    return JsonResponse(result)
