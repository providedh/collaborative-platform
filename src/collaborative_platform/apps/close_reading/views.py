import json
from urllib.parse import urlparse
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.urls import resolve

from apps.files_management.models import File
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def close_reading(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    origin, origin_url = get_origin(request, project_id)
    file = File.objects.get(project_id=project_id, id=file_id, deleted=False)
    project = file.project

    preferences = {
        'taxonomy': get_categories(project),
        'entities': get_entities(project),
        'properties_per_entity': get_entity_properties()
    }

    context = {
        'user_id': request.user.profile.get_xml_id(),
        'origin': origin,
        'origin_url': origin_url,
        'project_id': project.id,
        'file_id': file.id,
        'file_version': file.version_number,
        'title': file.name,
        'preferences': json.dumps(preferences),
        'DEVELOPMENT': False,
        'alerts': None,
    }

    return render(request, 'close_reading/close_reading.html', context)


def get_entity_properties() -> dict:
    from collaborative_platform.settings import DEFAULT_ENTITIES

    properties_per_entity = {
        key: {
            'properties': list(set(entity['properties'].keys()).difference('text')),
            'listable': entity['listable']
        }
        for key, entity in DEFAULT_ENTITIES.items()        
    }
    
    return properties_per_entity


def get_categories(project) -> dict:
    categories = {category.name: {
        'color': category.color,
        'desc': category.description
    } for category in
        project.taxonomy.categories.all()}

    return categories


def get_entities(project) -> dict:
    entities = {entity.name: {
        'color': entity.color,
        'icon': entity.icon
    } for entity in project.taxonomy.entities.all()}

    return entities


def get_origin(request: HttpRequest, project_id: str) -> (str, str):
    project_url = reverse('projects:files', args=[project_id])

    origin_url = request.META.get('HTTP_REFERER', project_url)
    if not origin_url.endswith('/'):
        origin_url += '/'

    try:
        resolve_match = resolve(urlparse(origin_url).path)
    except Exception as e:
        origin_url = project_url
        resolve_match = resolve(urlparse(origin_url).path)

    origin = resolve_match.url_name

    return origin, origin_url
