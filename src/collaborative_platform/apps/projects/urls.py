from django.urls import path
from . import views


urlpatterns = [
    path('<int:project_id>/delete/', views.delete, name='project_delete'),
    path('<int:project_id>/settings/', views.settings, name='project_settings'),
    path('<int:project_id>/files/', views.project_files, name='project_files'),
    path('<int:project_id>/', views.project, name='project'),
    path('user_autocomplete/', views.UserAutocomplete.as_view(), name='user_autocomplete'),
    path('', views.project, name='project_template'),
]
