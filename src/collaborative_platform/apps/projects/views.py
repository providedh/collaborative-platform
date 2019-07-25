from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, FieldError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from json import loads, JSONDecodeError

from .helpers import prepare_order_and_limits
from .models import Project, Contributor


@login_required(login_url="/login/")
def create(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == "POST" and request.body:
        try:
            data = loads(request.body)
        except JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

        try:
            if not data['title']:
                raise ValidationError

            project = Project(title=data['title'], description=data["description"])
            project.save()

            contributor = Contributor(project=project, user=request.user, permissions="AD")
            contributor.save()
            return HttpResponse("Success")
        except ValueError:
            return HttpResponseBadRequest("Possibly not logged in")
        except ValidationError:
            return HttpResponseBadRequest("Invalid value")

    return HttpResponseBadRequest("Invalid request type or empty request")


@login_required(login_url="/login/")
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


@login_required(login_url="/login/")
def get_yours(request):  # type: (HttpRequest) -> HttpResponse
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    order, start, end = prepare_order_and_limits(request)

    projects_ids = Contributor.objects.filter(user=request.user).values_list('project', flat=True)
    projects = Project.objects.filter(pk__in=projects_ids)

    if order is not None:
        try:
            projects = projects.order_by(*order)
        except FieldError:
            return HttpResponseBadRequest("Invalid order_by arguments")

    projects = list(projects[start:end].values())

    return JsonResponse(projects, safe=False)
