# import re
# import json
# from urllib.parse import urlparse
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from django.urls import reverse
# from django.urls import resolve

from apps.files_management.models import File
from apps.views_decorators import objects_exists, user_has_access


@login_required
@objects_exists
@user_has_access()
def close_reading(request, project_id, file_id):  # type: (HttpRequest, int, int) -> HttpResponse
    file = File.objects.get(project_id=project_id, id=file_id, deleted=False)

    # project_url = reverse('projects:files', args=[project_id])
    #
    # origin_url = request.META.get('HTTP_REFERER', project_url)
    # if not origin_url.endswith('/'):
    #     origin_url += '/'
    #
    # try:
    #     resolve_match = resolve(urlparse(origin_url).path)
    # except Exception as e:
    #     origin_url = project_url
    #     resolve_match = resolve(urlparse(origin_url).path)
    #
    # origin = resolve_match.url_name
    #
    # preferences = { 'taxonomy':{ }}
    # preferences['taxonomy'][file.project.taxonomy.name_1] = {
    #     'color': file.project.taxonomy.color_1,
    #     'desc': file.project.taxonomy.desc_1
    # }
    # preferences['taxonomy'][file.project.taxonomy.name_2] = {
    #     'color': file.project.taxonomy.color_2,
    #     'desc': file.project.taxonomy.desc_2
    # }
    # preferences['taxonomy'][file.project.taxonomy.name_3] = {
    #     'color': file.project.taxonomy.color_3,
    #     'desc': file.project.taxonomy.desc_3
    # }
    # preferences['taxonomy'][file.project.taxonomy.name_4] = {
    #     'color': file.project.taxonomy.color_4,
    #     'desc': file.project.taxonomy.desc_4
    # }

    context = {
        # 'origin': origin,
        # 'origin_url': origin_url,
        'title': file.name,
        'alerts': None,
        'file': file,
        'project_id': project_id,
        'file_id': file_id,
        # 'preferences': json.dumps(preferences)
    }

    return render(request, 'close_reading/close_reading.html', context)
