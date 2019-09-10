from django.urls import path
from . import views

urlpatterns = [
    path('<int:file_id>/', views.file, name='file'),
    path('<int:file_id>/version/<int:version>/', views.file, name='file_version'),
    path('<int:file_id>/versions', views.fileversions, name='fileversions'),
]
