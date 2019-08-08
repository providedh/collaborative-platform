from django.urls import path
from . import api

urlpatterns = [
    path('upload/', api.upload, name='upload'),
    path('<int:file_id>/versions/', api.get_file_versions, name='get_file_versions'),
]
