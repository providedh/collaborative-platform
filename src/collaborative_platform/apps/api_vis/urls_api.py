from django.urls import path
from . import api

urlpatterns = [
    path('projects/', api.projects),
    path('projects/<int:project_id>/history/', api.project_history),
    path('projects/<int:project_id>/files/<int:file_id>/body/', api.file_body),
    path('projects/<int:project_id>/files/<int:file_id>/meta/', api.file_meta),
    path('projects/<int:project_id>/files/<int:file_id>/names/', api.file_names),
    path('projects/<int:project_id>/files/<int:file_id>/annotations/', api.file_annotations),
    path('projects/<int:project_id>/files/<int:file_id>/people/', api.file_people),
    path('projects/<int:project_id>/files/<int:file_id>/', api.file),
    path('projects/<int:project_id>/files/', api.project_files),
    path('projects/<int:project_id>/context/<str:text>/', api.context_search),
    path('projects/<int:project_id>/cliques/<clique_id>/add/', api.add_to_clique),
    path('projects/<int:project_id>/cliques/', api.clique_creation),
]
