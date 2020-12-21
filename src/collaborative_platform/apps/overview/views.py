from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from apps.views_decorators import user_has_access
from apps.projects.models import Project

from . import helpers


@login_required
@user_has_access()
def main(request, project_id):  # type: (HttpRequest, int) -> HttpResponse
    project = Project.objects.get(pk=project_id)
    preferences = {
        'taxonomy': get_categories(project),
        'entities': get_entities(project)
    }

    return render(request, "overview/index.html", {
        "title":'Overview',
        "preferences": preferences,
        "project_name":project.title,
        "project_id":project_id,
        "DEVELOPMENT":False,
    })

@login_required
@user_has_access()
def get_versions(request, project_id):  # type: (HttpRequest, int) -> JSONResponse
    versions = helpers.get_project_versions(project_id)

    return JsonResponse({"versions": versions})

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
    } for entity in project.taxonomy.entities_schemas.all()}

    return entities
