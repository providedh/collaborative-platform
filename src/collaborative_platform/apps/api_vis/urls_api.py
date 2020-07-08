from django.urls import path
from . import api_OLD
from . import api


urlpatterns = [
    path('projects/', api_OLD.projects),
    path('projects/<int:project_id>/history/', api_OLD.project_history),
    path('projects/<int:project_id>/files/<int:file_id>/body/', api_OLD.file_body),
    path('projects/<int:project_id>/files/<int:file_id>/meta/', api_OLD.file_meta),
    path('projects/<int:project_id>/files/<int:file_id>/names/', api_OLD.file_names),
    path('projects/<int:project_id>/files/<int:file_id>/annotations/', api_OLD.file_annotations),
    path('projects/<int:project_id>/files/<int:file_id>/people/', api_OLD.file_people),
    path('projects/<int:project_id>/files/<int:file_id>/', api_OLD.file),
    path('projects/<int:project_id>/files/<int:file_id>/cliques/', api.file_cliques),
    path('projects/<int:project_id>/files/<int:file_id>/entities/unbound_entities/', api.file_unbound_entities),
    path('projects/<int:project_id>/files/<int:file_id>/entities/', api.file_entities),
    path('projects/<int:project_id>/files/', api_OLD.project_files),
    path('projects/<int:project_id>/context/<str:text>/', api_OLD.context_search),
    path('projects/<int:project_id>/cliques/<int:clique_id>/entities/', api.clique_entities),
    path('projects/<int:project_id>/cliques/', api.project_cliques),
    path('projects/<int:project_id>/commits/uncommitted_changes/', api.uncommitted_changes),
    path('projects/<int:project_id>/commits/', api.commits),
    path('projects/<int:project_id>/entities/unbound_entities/', api.project_unbound_entities),
    path('projects/<int:project_id>/entities/', api.project_entities),
]
