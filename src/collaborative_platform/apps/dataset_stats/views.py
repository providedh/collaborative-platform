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
def main(request, project_id):  # type: (HttpRequest, int, int) -> HttpResponse
    project = Project.objects.get(pk=project_id)
    return render(request, "dataset_stats/app.html", {
        "title":'TEI stats',
        "project_name":project.title,
        "project_id":project_id,
        "DEVELOPMENT":False,
    })
        
@login_required
@user_has_access()
def versions(request, project_id):  # type: (HttpRequest, int, float) -> JSONResponse
    data = {'project_versions': helpers.get_project_versions_files(project_id)}

    return JsonResponse(data)

@login_required
@user_has_access()
def stats(request, project_id, project_version):  # type: (HttpRequest, int, float) -> JSONResponse

    try:
        files = helpers.files_for_project_version(project_id, project_version)
        stats_df = helpers.create_summary_for_document_collection(files)
        stats = helpers.get_stats(stats_df)

        data = {'entities': stats, 'document_count': len(files), 'version': project_version}
    except ValueError:
        data = {"v": project_version, "entities": []}
    
    return JsonResponse(data)