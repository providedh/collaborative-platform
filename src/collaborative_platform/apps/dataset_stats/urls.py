from django.urls import path
from . import views

app_name = 'dataset_stats'

urlpatterns = [
	path('project/<int:project_id>/versions/', views.versions, name='versions'),
	path('project/<int:project_id>/version/<str:project_version>/stats/', views.stats, name='stats'),
    path('project/<int:project_id>/', views.main, name='main'),
]