from django.urls import path
from . import api

urlpatterns = [
    path('projects/<int:project_id>/proposals/', api.proposals),
    path('projects/<int:project_id>/proposals/details/', api.proposals_details),
    path('projects/<int:project_id>/files/<int:file_id>/proposals/', api.file_proposals),
    path('projects/<int:project_id>/calculations/', api.calculations),
    path('projects/<int:project_id>/tmp/', api.learn),  # TODO: remove this
]
