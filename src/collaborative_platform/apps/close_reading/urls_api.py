from django.urls import path
from . import api

urlpatterns = [
    path('project/<int:project_id>/file/<int:file_id>/save/', api.save, name='save'),
    path('project/<int:project_id>/file/<int:file_id>/version/<int:version>/history/', api.history, name='history'),
    path('current_user/', api.current_user, name='current_user'),
]
