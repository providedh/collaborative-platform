import re
import json
from urllib.parse import urlparse
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.urls import resolve

from apps.files_management.models import File
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def close_reading(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    file = File.objects.get(project_id=project_id, id=file_id, deleted=False)

    project_url = reverse('projects:files', args=[project_id])

    origin_url = request.META.get('HTTP_REFERER', project_url)
    if not origin_url.endswith('/'):
        origin_url += '/'

    try:
        resolve_match = resolve(urlparse(origin_url).path)
    except Exception as e:
        origin_url = project_url
        resolve_match = resolve(urlparse(origin_url).path)

    origin = resolve_match.url_name

    preferences = {'taxonomy': {category.name: {
        'color': category.color,
        'desc': category.description
    } for category in
        file.project.taxonomy.categories.all()}}

    context = {
        'origin': origin,
        'origin_url': origin_url,
        'title': file.name,
        'alerts': None,
        'file': file,
        'project_id': project_id,
        'file_id': file_id,
        'preferences': json.dumps(preferences),
        'DEVELOPMENT': False
    }

    return render(request, 'close_reading/close_reading.html', context)
