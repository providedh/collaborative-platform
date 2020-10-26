from django.urls import path
from . import api_old
from . import api


urlpatterns = [
    path('projects/', api_old.projects),
    path('projects/<int:project_id>/history/', api_old.project_history),
    path('projects/<int:project_id>/certainties/', api.project_certainties),
    path('projects/<int:project_id>/files/<int:file_id>/body/', api_old.file_body),
    path('projects/<int:project_id>/files/<int:file_id>/meta/', api_old.file_meta),
    path('projects/<int:project_id>/files/<int:file_id>/names/', api_old.file_names),
    path('projects/<int:project_id>/files/<int:file_id>/', api_old.file),
    path('projects/<int:project_id>/files/<int:file_id>/cliques/', api.file_cliques),
    path('projects/<int:project_id>/files/<int:file_id>/entities/unbound_entities/', api.file_unbound_entities),
    path('projects/<int:project_id>/files/<int:file_id>/entities/', api.file_entities),
    path('projects/<int:project_id>/files/<int:file_id>/certainties/', api.file_certainties),
    path('projects/<int:project_id>/files/', api_old.project_files),
    path('projects/<int:project_id>/context/<str:text>/', api_old.context_search),
    path('projects/<int:project_id>/cliques/<int:clique_id>/entities/', api.clique_entities),
    path('projects/<int:project_id>/cliques/', api.project_cliques),
    path('projects/<int:project_id>/commits/uncommitted_changes/', api.uncommitted_changes),
    path('projects/<int:project_id>/commits/', api.commits),
    path('projects/<int:project_id>/entities/unbound_entities/', api.project_unbound_entities),
    path('projects/<int:project_id>/entities/', api.project_entities),
]
