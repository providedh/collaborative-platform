from django.urls import path
from . import api

urlpatterns = [
    path('projects/', api.projects),
    path('projects/<int:project_id>/history/', api.project_history),
    path('projects/<int:project_id>/files/<int:file_id>/', api.file),
    path('projects/<int:project_id>/files/', api.project_files),
]
