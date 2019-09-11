from django.urls import path
from . import views

urlpatterns = [
    path('user_projects/<int:user_id>/', views.projects, name='projects'),
    path('<int:project_id>/contributors/', views.contributors, name='contributors'),
    path('<int:project_id>/', views.project, name='project'),
    path('user_autocomplete/', views.UserAutocomplete.as_view(), name='user_autocomplete'),
    path('', views.project, name='project_template'),
]
