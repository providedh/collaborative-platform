from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, FieldError
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, \
    HttpResponseForbidden
from json import loads, JSONDecodeError, dumps

from apps.projects.helpers import page_to_json_response
from .helpers import paginate, order_queryset
from .models import Project, Contributor


@login_required()
def create(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.body:
        try:
            data = loads(request.body)
        except JSONDecodeError:
            return HttpResponseBadRequest(dumps({"message": "Invalid JSON"}))

        try:
            if not data['title']:
                raise ValidationError

            project = Project(title=data['title'], description=data["description"])
            project.save()

            contributor = Contributor(project=project, user=request.user, permissions="AD")
            contributor.save()
            return HttpResponse(dumps({"id": project.id}))
        except ValueError:
            return HttpResponseBadRequest(dumps({"message": "Possibly not logged in"}))
        except (ValidationError, KeyError):
            return HttpResponseBadRequest(dumps({"message": "Invalid value"}))

    return HttpResponseBadRequest(dumps({"message": "Invalid request type or empty request"}))


@login_required()
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

    return page_to_json_response(page)


@login_required()
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

    return page_to_json_response(page)


@login_required()
def get_activities(request, project_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    try:
        project = Project.objects.filter(id=project_id).get()
    except Project.DoesNotExist:
        return HttpResponseNotFound("Project with given id does not exist")

    if not project.public:
        try:
            project.contributors.filter(user_id=request.user.id).get()
        except Contributor.DoesNotExist:
            return HttpResponseForbidden("User has no access to a project")

    activities = project.activities.order_by("-date")
    try:
        page = paginate(request, activities)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return page_to_json_response(page)
