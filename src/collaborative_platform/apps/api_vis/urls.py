from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.projects),
    path('projects/<int:project_id>/history/', views.project_history),
    path('projects/<int:project_id>/files/', views.project_files),
]
