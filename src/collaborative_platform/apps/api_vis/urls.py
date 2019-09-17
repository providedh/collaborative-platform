from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/history/', views.project_history, name='project_history'),
    path('projects/<int:project_id>/files/', views.project_files, name='project_files'),
]
