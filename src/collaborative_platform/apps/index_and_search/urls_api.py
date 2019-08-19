from django.urls import path
from . import api

urlpatterns = [
    path('entity_completion/project/<int:project_id>/entity/<str:entity_type>/<str:query>', api.entity_completion,
         name='entity_completion'),
]
