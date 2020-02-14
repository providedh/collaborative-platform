from django.urls import path
from . import views

app_name = 'vis_dashboard'

urlpatterns = [
	path('project/<int:project_id>/create/', views.dashboard_create, name='create'),
	path('project/<int:project_id>/vis/<int:dashboard_id>/', views.get_dashboard, name='app'),
	path('project/<int:project_id>/vis/<int:dashboard_id>/edit/', views.dashboard_edit, name='edit'),
	path('project/<int:project_id>/vis/<int:dashboard_id>/update/', views.dashboard_update, name='update'),
	path('project/<int:project_id>/vis/<int:dashboard_id>/delete/', views.dashboard_delete, name='delete'),
    path('project/<int:project_id>/', views.dashboard_list, name='list'),
]