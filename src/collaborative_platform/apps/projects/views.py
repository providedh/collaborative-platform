from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from json import loads, JSONDecodeError

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

    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 5)
    per_page = min(per_page, 50)  # limited for safety reasons

    start = (page - 1) * per_page
    end = start + per_page + 1

    projects = list(Project.objects.filter(public=True)[start:end].values())

    return JsonResponse(projects, safe=False)
