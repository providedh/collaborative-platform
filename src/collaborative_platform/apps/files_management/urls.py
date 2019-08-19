from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('<int:file_id>/', views.file, name='file'),
    path('<int:file_id>/version/<int:version>/', views.file, name='file_version'),
]
