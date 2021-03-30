from django.urls import path
from . import views

urlpatterns = [
    path('project/<int:project_id>/', views.disambiguator_ui, name='disambiguator_ui'),
]