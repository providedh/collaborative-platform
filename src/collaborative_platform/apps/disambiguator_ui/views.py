import json
from urllib.parse import urlparse
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from apps.projects.models import Project
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def disambiguator_ui(request, project_id):  # type: (HttpRequest, int, int) -> HttpResponse
    project = Project.objects.get(id=project_id)
    preferences = {
        'taxonomy': get_categories(project),
        'entities': get_entities(project),
        'properties_per_entity': get_entity_properties()
    }

    context = {
        'user_id': request.user.profile.get_xml_id(),
        'project_id': project.id,
        'project_name': project.title,
        'preferences': json.dumps(preferences),
        'DEVELOPMENT': True,
        'alerts': None,
    }

    return render(request, 'disambiguator_ui/index.html', context)


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
        'icon': entity.icon,
        'listable': entity.body_list,
    } for entity in project.taxonomy.entities.all()}

    return entities
