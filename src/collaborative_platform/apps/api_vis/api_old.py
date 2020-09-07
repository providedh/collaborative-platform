import xmltodict
import apps.index_and_search.models as es

from lxml import etree

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse

from collaborative_platform.settings import XML_NAMESPACES

from apps.files_management.api import download_file as files_management__download_file
from apps.files_management.models import File, FileVersion
from apps.projects.models import Contributor
from apps.views_decorators import objects_exists, user_has_access

from .helpers import search_files_by_person_name, search_files_by_content


ANNOTATION_TAGS = ['date', 'event', 'location', 'geolocation', 'name', 'occupation', 'object', 'org', 'person', 'place',
                   'country', 'time']


@login_required
def projects(request):  # type: (HttpRequest) -> JsonResponse
    if request.method == 'GET':
        user = request.user

        contributors = Contributor.objects.filter(user=user)

        response = []

        for contributor in contributors:
            project = {
                'id': contributor.project.id,
                'name': contributor.project.title,
                'permissions': contributor.permissions,
            }

            response.append(project)

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def project_history(request, project_id):  # type: (HttpRequest, int) -> JsonResponse
    if request.method == 'GET':
        response = {  # TODO: not implemented
            'info': 'Not implemented. Need to agree an appearance of response.'
        }

        return JsonResponse(response, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def project_files(request, project_id):  # type: (HttpRequest, int) -> JsonResponse
    if request.method == 'GET':
        search = request.GET.get('search', None)
        person = request.GET.get('person', None)

        if search:
            return search_files_by_content(request, project_id, search)

        elif person:
            return search_files_by_person_name(request, project_id, person)

        else:
            files = File.objects.filter(project=project_id, deleted=False).order_by('id')

            response = []

            for file in files:
                file_details = {
                    'id': file.id,
                    'name': file.name,
                    'path': file.get_relative_path(),
                }

                response.append(file_details)

            return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def file(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        response = files_management__download_file(request, file_id)

        return response


@login_required
@objects_exists
@user_has_access()
def file_body(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        file_version = FileVersion.objects.get(file=file, number=file.version_number)
        file_path = file_version.upload.path

        with open(file_path) as file:
            xml_content = file.read()

        tree = etree.fromstring(xml_content)
        body = tree.xpath('//default:text/default:body', namespaces=XML_NAMESPACES)[0]
        text_nodes = body.xpath('.//text()')
        plain_text = ''.join(text_nodes)

        return HttpResponse(plain_text, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def file_meta(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    if request.method == 'GET':
        file = File.objects.get(id=file_id, deleted=False)
        file_version = FileVersion.objects.get(file=file, number=file.version_number)
        file_path = file_version.upload.path

        with open(file_path) as file:
            xml_content = file.read()

        parsed_xml = xmltodict.parse(xml_content)
        response = parsed_xml['TEI']['teiHeader']

        return JsonResponse(response, status=HttpResponse.status_code, safe=False)


@login_required
@objects_exists
@user_has_access()
def file_names(request, project_id, file_id):  # type: (HttpRequest, int, int) -> JsonResponse
    if request.method == 'GET':
        response = {
            'info': 'Not implemented.'
        }

        return JsonResponse(response, status=HttpResponse.status_code)


@login_required
@objects_exists
@user_has_access()
def context_search(request, project_id, text):  # type: (HttpRequest, int, str) -> HttpResponse
    r = es.File.search().filter('term', project_id=project_id).highlight('text').query('match', text=text).execute()

    response = []
    for hit in r:
        file = File.objects.get(id=hit.id, deleted=False)
        response.append({
            'file': {
                'name': file.name,
                'path': file.get_path(),
                'id': file.id
            },
            'contexts': [fragment for fragment in hit.meta.highlight.text]
        })

    return JsonResponse(response, safe=False)
