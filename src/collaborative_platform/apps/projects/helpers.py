from json import loads, dumps
from typing import Iterable, Dict, Union

from django.contrib.auth.models import User
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseBadRequest

from apps.files_management.models import File, Directory
from apps.projects.models import Activity, Project, Contributor


def paginate_page_perpage(request, queryset):  # type: (HttpRequest, QuerySet) -> Page
    queryset = queryset.values()
    page = request.GET.get("page")
    if page is None:
        return Paginator(queryset, len(queryset) or 1, allow_empty_first_page=True).page(1)

    page = int(page)
    per_page = int(request.GET.get("per_page", 10))

    return Paginator(queryset, per_page or 1, allow_empty_first_page=True).page(page)


# TODO: checking if those arguiments are given
def paginate_start_length(request, queryset):  # type: (HttpRequest, QuerySet) -> Page
    start = int(request.GET.get("start") or 0)
    length = int(request.GET.get("length") or 0)
    if length:
        queryset = queryset[start: start + length + 1].values()
    else:
        queryset = queryset.values()
        length = len(queryset)
    return Paginator(queryset, length, allow_empty_first_page=True).page(1)


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
        "data": list(page.object_list)
    }
    return JsonResponse(response, safe=False)


def get_project_contributors(project_id):  # type: (int) -> QuerySet
    ids = Project.objects.filter(id=project_id).get().contributors.values_list('user', flat=True)
    return User.objects.filter(id__in=ids)


def include_contributors(response):  # type: (JsonResponse) -> JsonResponse
    json = loads(response.content)
    for project in json['data']:
        project['contributors'] = list(get_project_contributors(project['id']).values('id', 'first_name', 'last_name'))

    return JsonResponse(json)


def log_activity(project, user, action_text="", file=None,
                 related_dir=None):  # type: (Project, User, str, File, Directory) -> Activity
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


def update_contributor(project_id, user_id, level, delete=False):  # type: (int, int, str, bool) -> None
    try:
        c = Contributor.objects.filter(project_id=project_id, user_id=user_id).get()
        if delete:
            c.delete()
            return
    except Contributor.DoesNotExist():
        c = Contributor(project_id=project_id, user_id=user_id, level=level)
        c.save()
        return
    else:
        c.level = level
        c.save()


def update_contributors(project_id, contributors):
    # type: (int, Iterable[Dict[str, Union[int, str, bool]]]) -> HttpResponse
    if 'AD' not in (c['level'] for c in contributors):
        return HttpResponseBadRequest(dumps({"message": "There must be at least one administrator in a project."}))

    for contrib in contributors:
        update_contributor(project_id, **contrib)

    return HttpResponse("OK")
