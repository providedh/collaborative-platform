from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('<int:file_id>/version/<int:version_nr>/', views.file, name='file'),
]
