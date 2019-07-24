from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
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

        project = Project(title=data["title"], description=data["description"])
        project.save()

        contributor = Contributor(project=project, user=request.user, permissions="AD")
        contributor.save()

    return HttpResponseBadRequest("Invalid request type or empty request")
