from json import loads, JSONDecodeError, dumps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError, FieldError
from django.core.paginator import InvalidPage, EmptyPage
from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse

from apps.files_management.helpers import clean_name
from apps.files_management.models import Directory
from apps.logging_functions import log_creating_project, log_adding_user_to_project
from apps.projects.helpers import page_to_json_response, include_contributors, log_activity, paginate_start_length, \
    get_contributors_list
from apps.views_decorators import objects_exists, user_has_access

from .helpers import paginate_page_perpage, order_queryset
from .models import Project, Contributor, Taxonomy, UncertaintyCategory, EntitySchema


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

            project_name = clean_name(data['title'])

            project = Project(title=project_name, description=data["description"])
            project.save()

            create_taxonomy(data, project)

            log_creating_project(project.id, request.user.id, data)

            contributor = Contributor(project=project, user=request.user, permissions="AD",
                                      profile=request.user.profile)
            contributor.save()

            log_adding_user_to_project(project.id, request.user.id, "AD")

            project_directory = Directory(name=project_name, project=project)
            project_directory.save()

            log_activity(project, request.user, "created project")

            return HttpResponse(dumps({"id": project.id}))

        except (ValidationError, KeyError):
            return HttpResponseBadRequest(dumps({"message": "Invalid value"}))

    return HttpResponseBadRequest(dumps({"message": "Invalid request type or empty request"}))


def create_taxonomy(data, project):
    taxonomy_data = data['taxonomy']
    for cat in taxonomy_data:
        cat["xml_id"] = '-'.join(cat['name'].lower().strip().split())
    taxonomy = Taxonomy(project=project)
    taxonomy.save()

    UncertaintyCategory.objects.bulk_create(
        UncertaintyCategory(taxonomy=taxonomy, **cat) for cat in taxonomy_data
    )

    taxonomy.update_contents()

    EntitySchema.objects.bulk_create(
        EntitySchema(taxonomy=taxonomy, **entity) for entity in data['entities']
    )


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
def get_contributors(request, project_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")
    return JsonResponse(get_contributors_list(project_id), safe=False)


@login_required
@objects_exists
@user_has_access()
def get_taxonomy(request, project_id):
    if request.method != "GET":
        return HttpResponseBadRequest("Invalid request method")

    project = Project.objects.get(id=project_id)
    return HttpResponse(project.taxonomy.contents, content_type="application/xml")


@login_required
@objects_exists
@user_has_access()
def get_settings(request, project_id):
    entities = EntitySchema.objects.filter(taxonomy__project_id=project_id).values("name", "color", "icon")
    uncertainty_cats = UncertaintyCategory.objects.filter(taxonomy__project_id=project_id).values("name", "xml_id",
                                                                                                  "color",
                                                                                                  "description")

    resp = {"entities": list(entities),
            "taxonomy": list(uncertainty_cats)}

    return JsonResponse(resp)


@login_required
def get_default_properties(request):
    from collaborative_platform.settings import DEFAULT_ENTITIES

    properties_per_entity = {
        key: {'properties': list(set(entity['properties'].keys()).difference('text'))}
        for key, entity in DEFAULT_ENTITIES.items()        
    }
    
    return JsonResponse(properties_per_entity)
