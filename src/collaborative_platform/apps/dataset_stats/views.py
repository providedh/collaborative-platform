from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from apps.views_decorators import objects_exists, user_has_access
from apps.files_management.models import File, FileVersion
from apps.projects.models import Project, ProjectVersion

from django.db.models import Q

from . import helpers

@login_required
@user_has_access()
def main(request, project_id=1):  # type: (HttpRequest, int, int) -> HttpResponse
    project = Project.objects.get(pk=project_id)
    files_query = Q(project=project)
    files = File.objects.filter(files_query)

    get_latest_content = lambda f: f.versions \
        .latest('creation_date') \
        .get_content() \
        .split('<?xml version="1.0"?>')[1] \
        .strip()

    return render(request, "dataset_stats/app.html", {
        "title":project.title, 
        "project_id":project_id,
        "DEVELOPMENT":True,
        "tags": [],
        "document_count": len(files),
    })
        
    file_gen = ((get_latest_content(file), file.name) for file in files)
    stats_df = helpers.create_summary_for_document_collection(file_gen)
    tags = helpers.get_stats(stats_df)

    content = {
    	"title":project.title, 
    	"project_id":project_id,
    	"DEVELOPMENT":True,
    	"tags": tags,
    	"document_count": len(files),
    }

    return render(request, "dataset_stats/app.html", content)

@login_required
@user_has_access()
def versions(request, project_id=1):  # type: (HttpRequest, int, float) -> JSONResponse
    data = {'project_versions': helpers.get_project_versions_files(project_id)}

    return JsonResponse(data)

@login_required
@user_has_access()
def stats(request, project_id, project_version):  # type: (HttpRequest, int, float) -> JSONResponse
    data = {}

    try:
        version_num = float(project_version)
        #versions = ProjectVersion.objects.filter()
        data = {'version': version_num, 'entities': [
            {
                'name': 'place',
                'count': 12,
                'coverage': 30,
                'location': 'header',
                'distinct_doc_occurrences': 3,
                'document_count': 10,
                'attributes': []
            },
            {
                'name': 'person',
                'count': 22,
                'coverage': 80,
                'location': 'body',
                'distinct_doc_occurrences': 8,
                'document_count': 10,
                'attributes': [
                    {
                        'name': 'age',
                        'distinct_values': 3,
                        'trend_percentage': 80,
                        'trend_value': 35,
                        'coverage': 30
                    }
                ]
            }
            ]}
    except ValueError:
        data = {v: project_version, entities: []}
    
    return JsonResponse(data)