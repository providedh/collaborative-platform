from json import loads

from django.contrib.auth.models import User
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse

from apps.projects.models import Activity, Project


def paginate(request, queryset):  # type: (HttpRequest, QuerySet) -> Page
    queryset = queryset.values()
    page = request.GET.get("page")
    if page is None:
        return Paginator(queryset, len(queryset), allow_empty_first_page=True).page(1)

    page = int(page)
    per_page = int(request.GET.get("per_page", 10))

    return Paginator(queryset, per_page, allow_empty_first_page=True).page(page)


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
