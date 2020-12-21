from django.urls import path
from . import views


app_name = 'overview'

urlpatterns = [
    path('project/<int:project_id>/api/', views.get_versions, name='api'),
    path('project/<int:project_id>/', views.main, name='main'),
]
