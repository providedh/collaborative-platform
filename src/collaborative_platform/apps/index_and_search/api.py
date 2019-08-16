from django.contrib.auth.decorators import login_required
from django.http import HttpRequest


@login_required()
def entity_completion(request, entity_type, query):  # type: (HttpRequest, str, str) -> HttpRequest
    return None
