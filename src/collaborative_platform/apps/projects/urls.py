from django.urls import path
from . import views

urlpatterns = [
    path('user_projects/<int:user_id>/', views.projects, name='projects'),
    path('<int:project_id>/', views.project, name='project'),
]
