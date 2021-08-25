from django.urls import path
from . import views

urlpatterns = [
    path('project/<int:project_id>/file/<int:file_id>/', views.poetry_analysis, name='poetry_analysis'),
]
