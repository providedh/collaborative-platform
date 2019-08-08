from django.core.paginator import Paginator, Page
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse

from apps.projects.models import Activity


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
