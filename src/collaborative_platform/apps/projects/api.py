from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, FieldError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from json import loads, JSONDecodeError, dumps

from .helpers import prepare_order_and_limits
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

    order, start, end = prepare_order_and_limits(request)

    projects = Project.objects.filter(public=True)

    if order is not None:
        try:
            projects = projects.order_by(*order)
        except FieldError:
            return HttpResponseBadRequest("Invalid order_by arguments")

    projects = list(projects[start:end].values())

    return JsonResponse(projects, safe=False)


@login_required()
def get_mine(request):  # type: (HttpRequest) -> HttpResponse
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    order, start, end = prepare_order_and_limits(request)

    projects_ids = request.user.contributions.values_list('project', flat=True)
    projects = Project.objects.filter(pk__in=projects_ids)

    if order is not None:
        try:
            projects = projects.order_by(*order)
        except FieldError:
            return HttpResponseBadRequest("Invalid order_by arguments")

    projects = list(projects[start:end].values())

    return JsonResponse(projects, safe=False)
