import time
from json import loads

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet, F
from django.http import HttpRequest, JsonResponse
from django.urls import reverse

from apps.api_vis.models import Commit
from apps.files_management.models import Directory, File, FileVersion
from apps.projects.models import Activity, Project, ProjectVersion, Contributor
import logging

logger = logging.getLogger('upload')


def paginate_page_perpage(request, queryset):  # type: (HttpRequest, QuerySet) -> Page
    queryset = queryset.values()
    page = request.GET.get("page")
    if page is None:
        return Paginator(queryset, len(queryset) or 1, allow_empty_first_page=True).page(1)

    page = int(page)
    per_page = int(request.GET.get("per_page", 10))

    return Paginator(queryset, per_page or 1, allow_empty_first_page=True).page(page)


def paginate_start_length(request, queryset):  # type: (HttpRequest, QuerySet) -> Page
    start = int(request.GET.get("start") or 0)
    length = int(request.GET.get("length") or 10)
    page_nr = int(start / length) + 1
    return Paginator(queryset.values(), length, allow_empty_first_page=True).page(page_nr)


def order_queryset(request, queryset):  # type: (HttpRequest, QuerySet) -> QuerySet
    order = request.GET.get("order")
    if order is not None:
        order = tuple(map(str.strip, order.split(',')))
        queryset = queryset.order_by(*order)

    return queryset


def page_to_json_response(page):  # type: (Page) -> JsonResponse
    response = {
        "pages": page.paginator.num_pages,
        "per_page": page.paginator.per_page,
        "current_page": page.number,
        "entries": len(page),
        "recordsTotal": page.paginator.count,
        "recordsFiltered": page.paginator.count,
        "data": list(page.object_list)
    }
    return JsonResponse(response, safe=False)


def get_project_contributors(project_id):  # type: (int) -> QuerySet
    ids = Project.objects.get(id=project_id).contributors.values_list('user', flat=True)
    return User.objects.filter(id__in=ids)


def include_contributors(response):  # type: (JsonResponse) -> JsonResponse
    json = loads(response.content)
    for project in json['data']:
        project['contributors'] = get_contributors_list(project['id'])

    return JsonResponse(json)


def get_contributors_list(project_id):
    return list(get_project_contributors(project_id).values('id', 'first_name', 'last_name'))


def log_activity(project, user, action_text="", file=None, related_dir=None):
    # type: (Project, User, str, File, Directory) -> Activity

    a = Activity(project=project, user=user, user_name="{} {}".format(user.first_name, user.last_name),
                 action_text=action_text)
    if file is not None:
        a.related_file = file
        a.related_file_name = file.name
    if related_dir is not None:
        a.related_dir = related_dir
        a.related_dir_name = related_dir.name
    a.save()
    return a


def create_new_project_version(project, files_modification=False, commit=None):
    # type: (Project, bool, Commit) -> None
    dt = time.time()
    latest_file_versions = FileVersion.objects.filter(file__project=project, file__version_number=F('number'))
    project_versions = ProjectVersion.objects.filter(project=project)

    if project_versions.exists():
        latest_project_version = project_versions.latest('id')

        file_version_counter = latest_project_version.file_version_counter + int(files_modification)
        commit_counter = latest_project_version.commit_counter + int(commit is not None)

        new_project_version = ProjectVersion(file_version_counter=file_version_counter,
                                             commit=commit,
                                             commit_counter=commit_counter,
                                             project=project)
        new_project_version.save()
        new_project_version.file_versions.set(latest_file_versions)
        new_project_version.save()

    else:
        new_project_version = ProjectVersion(file_version_counter=0, commit=commit, commit_counter=0, project=project)
        new_project_version.save()
        new_project_version.file_versions.set(latest_file_versions)
        new_project_version.save()
    logger.info(f"create_new_project_version took {time.time() - dt} s")
