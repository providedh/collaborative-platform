from django.urls import path
from . import views

urlpatterns = [
    path('<int:project_id>/<int:file_id>/', views.close_reading, name='close_reading'),
]
