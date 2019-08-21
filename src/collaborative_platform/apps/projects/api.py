from json import loads, JSONDecodeError, dumps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, FieldError
from django.core.paginator import InvalidPage, EmptyPage
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from apps.files_management.models import Directory
from apps.projects.helpers import page_to_json_response, include_contributors, log_activity
from apps.views_decorators import objects_exists, user_has_access

from .helpers import paginate, order_queryset
from .models import Project, Contributor


@login_required
def create(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.body:
        try:
            data = loads(request.body)
        except JSONDecodeError:
            return HttpResponseBadRequest(dumps({"message": "Invalid JSON"}))

        try:
            if not data['title']:
                return HttpResponseBadRequest(dumps({"message": "Title cannot be empty"}))

            project = Project(title=data['title'], description=data["description"])
            project.save()

            contributor = Contributor(project=project, user=request.user, permissions="AD")
            contributor.save()

            base_dir = Directory(name=data['title'], project=project)
            base_dir.save()

            log_activity(project, request.user, "created")
            return HttpResponse(dumps({"id": project.id}))
        except (ValidationError, KeyError):
            return HttpResponseBadRequest(dumps({"message": "Invalid value"}))

    return HttpResponseBadRequest(dumps({"message": "Invalid request type or empty request"}))


@login_required
def get_public(request):  # type: (HttpRequest) -> HttpResponse
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    projects = Project.objects.filter(public=True)

    try:
        projects = order_queryset(request, projects)
    except FieldError:
        return HttpResponseBadRequest(dumps({"message": "Invalid order_by argument"}))

    try:
        page = paginate(request, projects)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return include_contributors(page_to_json_response(page))


@login_required
def get_mine(request):  # type: (HttpRequest) -> HttpResponse
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    projects_ids = request.user.contributions.values_list('project', flat=True)
    projects = Project.objects.filter(pk__in=projects_ids)

    projects = order_queryset(request, projects)
    try:
        page = paginate(request, projects)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return include_contributors(page_to_json_response(page))


@login_required
@objects_exists
@user_has_access()
def get_activities(request, project_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    project = Project.objects.filter(id=project_id).get()

    activities = project.activities.order_by("-date")
    try:
        page = paginate(request, activities)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return page_to_json_response(page)
