from json import loads, JSONDecodeError, dumps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError, FieldError
from django.core.paginator import InvalidPage, EmptyPage
from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from apps.core.models import Profile
from apps.files_management.models import Directory
from apps.projects.helpers import page_to_json_response, include_contributors, log_activity, paginate_start_length
from apps.views_decorators import objects_exists, user_has_access

from .helpers import paginate_page_perpage, order_queryset
from .models import Project, Contributor, Taxonomy


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
            print(data)
            project = Project(title=data['title'], description=data["description"])
            project.save()

            taxonomy_data = {key[9:]: val for key, val in data.items() if key.startswith("taxonomy.")}
            for key, val in taxonomy_data.items():
                if key.startswith("taxonomy.xml_id"):
                    taxonomy_data[key] = '-'.join(val.lower().strip().split())
            taxonomy = Taxonomy(project=project, **taxonomy_data)
            taxonomy.save()

            profile = Profile.objects.get(user=request.user)

            contributor = Contributor(project=project, user=request.user, permissions="AD", profile=profile)
            contributor.save()

            base_dir = Directory(name=data['title'], project=project)
            base_dir.save()

            log_activity(project, request.user, "created project")
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
        page = paginate_page_perpage(request, projects)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return include_contributors(page_to_json_response(page))


@login_required
def get_mine(request):  # type: (HttpRequest) -> HttpResponse
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    projects = get_user_projects(request.user)

    projects = order_queryset(request, projects)
    try:
        page = paginate_page_perpage(request, projects)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return include_contributors(page_to_json_response(page))


@login_required
@objects_exists
@user_has_access()
def get_activities(request, project_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    project = Project.objects.get(id=project_id)

    activities = project.activities.order_by("-date")
    try:
        page = paginate_start_length(request, activities)
    except (ZeroDivisionError, InvalidPage, EmptyPage):
        return HttpResponseNotFound(dumps({"message": "Invalid page number"}))

    return page_to_json_response(page)


def get_user_projects(user):  # type: (User) -> QuerySet
    projects_ids = user.contributions.values_list('project', flat=True)
    projects = Project.objects.filter(pk__in=projects_ids)
    return projects


def get_users(request, user_id):  # type: (HttpRequest, int) -> HttpResponse
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest("Invalid user ID")

    if type(request.user) == AnonymousUser:
        projects = get_user_projects(user).filter(public=True)
    else:
        requestor_projects = get_user_projects(request.user).values_list('id', flat=True)
        projects = get_user_projects(user).filter(Q(public=True) | Q(id__in=requestor_projects))

    projects = order_queryset(request, projects)
    page = paginate_start_length(request, projects)
    return include_contributors(page_to_json_response(page))


@login_required
@objects_exists
@user_has_access()
def get_taxonomy(request, project_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    project = Project.objects.get(id=project_id)
    return HttpResponse(project.taxonomy.contents)
