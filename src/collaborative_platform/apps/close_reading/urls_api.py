from django.urls import path
from . import api

urlpatterns = [
    path('<int:project_id>/<int:file_id>/save/', api.save, name='save'),
    path('<int:project_id>/<int:file_id>/<int:file_version>/annotation_history/', api.annotation_history,
         name='annotation_history'),
]
